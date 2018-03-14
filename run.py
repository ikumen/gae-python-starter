from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from server import api

app = DispatcherMiddleware(api.create_app())