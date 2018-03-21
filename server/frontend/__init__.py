from .. import create_app as factory_create_app

def create_app(settings_override=None):
   """Creates API specific application instance.
   """
   app = factory_create_app(__name__, __path__, settings_override)
   return app
