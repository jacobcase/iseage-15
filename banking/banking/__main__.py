import logging
import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from banking import app

SESSION_KEY = "1234"
PORT = 80


if __name__ != '__main__':
    logging.error("Run module directly ex: python3 -m banking")
    sys.exit(2)

# TODO: store in database or load from protect file, used for protecting session keys
#  OR we can implement a custom session
app.secret_key = SESSION_KEY

# TODO: SSL??
http_server = HTTPServer(WSGIContainer(app))

# TODO: WAT PORTS??
http_server.listen(PORT)

IOLoop.instance().start()

