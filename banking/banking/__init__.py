import logging
from flask import Flask

logging.info("Creating flask app")
app = Flask(__name__, static_url_path='')
app.debug = True

logging.info("Loading views")
import banking.views

