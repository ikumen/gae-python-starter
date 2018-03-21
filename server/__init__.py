import importlib
import os
import pkgutil

from flask import Flask, Blueprint
from flask.json import JSONEncoder
from .helpers import JSONSerializableEncoder
from .config import load_settings, GAEDataStoreConfiguration
from .security import oauth_factory
from . import models
from . import constants


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package.

    @param app the Flask application
    @param pkg_name name of package
    @param pkg_path path where package is located
    """
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)


def create_app(pkg_name, pkg_path, override_settings=None):
    """Return a basic Flask application instance configured with defaults.

    @param pkg_name name of package
    @param pkg_path path where package is located
    @param settings_override dictionary of settings
    """ 
    app = Flask(pkg_name)

    # custom json encoder
    app.json_encoder = JSONSerializableEncoder

    # initialize database and bootstrap any data
    init_db(app)

    # initialize and load config settings
    load_settings(app, GAEDataStoreConfiguration, override_settings=override_settings)

    # initialize security
    init_security(app)
    
    # register blueprint modules
    _register_blueprints(app, pkg_name, pkg_path)

    return app

def init_security(app):
    """Configures application security.
    """
    if 'OAUTH' not in app.config:
        raise RuntimeError('{} configuration missing!'.format('OAUTH'))
    oauth_factory.init_config(app.config['OAUTH'])


def init_db(app):
    pass