import tornado.web
import tornado.ioloop
from TornadoSSEHandler import TornadoSSEHandler

def make_app():
    return tornado.web.Application([
        (r"/sse/chat", TornadoSSEHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()