from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from server import api, frontend

app = DispatcherMiddleware(frontend.create_app(), {
        '/api': api.create_app()
    })