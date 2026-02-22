from aiohttp import web
from tgfs.routes import routes

def init_routes(app: web.Application):
    app.add_routes(routes)

init_handlers = [init_routes]
def init_app() -> web.Application:
    app = web.Application()

    for init in init_handlers:
        init(app)
    return app
