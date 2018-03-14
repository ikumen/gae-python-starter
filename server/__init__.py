import pkgutil
import importlib

from flask import Flask, Blueprint
from flask.json import JSONEncoder
from .helpers import JSONSerializableEncoder
from . import models
from . import settings


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


def create_app(pkg_name, pkg_path, settings_override=None):
    """Return a basic Flask application instance configured with defaults.

    @param pkg_name name of package
    @param pkg_path path where package is located
    @param settings_override dictionary of settings
    """ 
    app = Flask(pkg_name)

    app.config.from_object(settings) # loads the default settings
    app.config.from_object(settings_override) # optional overrides
    app.config.from_pyfile('local.settings', silent=True) # environment specific overrides
    
    app.json_encoder = JSONSerializableEncoder
    _register_blueprints(app, pkg_name, pkg_path)

    return app
