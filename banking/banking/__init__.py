import logging
from flask import Flask
import base64
from itsdangerous import TimestampSigner, SignatureExpired
import os

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(module)s: %(message)s",
    level="INFO"
)

logging.info("Creating flask app")
app = Flask(__name__, static_url_path='')
app.debug = True

#TODO: make key perm to survive restarts
#signer = TimestampSigner(base64.b64encode(os.urandom(32)))
signer = TimestampSigner("temp")

logging.info("Loading views")
import banking.views

