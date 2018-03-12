import os

from flask import Flask, json
from . import models
from . import settings

class JSONEncoder(json.JSONEncoder):
   def default(self, obj):
      if isinstance(obj, models.AbstractModel):
         data = obj.to_dict()
         if hasattr(obj, 'key'):
            data['key'] = obj.key.urlsafe()
         return data
      return json.JSONEncoder.default(self, obj)


def create_app(app_name=None, opt_settings=None):
   app = Flask(__name__)

   app.config.from_object(settings) # loads the default settings
   app.config.from_object(opt_settings) # optional overrides
   app.config.from_pyfile('local.settings', silent=True) # environment specific overrides
   app.json_encoder = JSONEncoder

   configure_db(app)
   configure_blueprints(app)
   configure_cli(app)

   return app


def configure_blueprints(app):
   from api import bp as api_bp
   for bp in [api_bp]:
      app.register_blueprint(bp)


def configure_db(app):
   pass


def configure_cli(app):
   pass
