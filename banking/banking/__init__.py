import logging
from flask import Flask
import base64
from itsdangerous import TimestampSigner, SignatureExpired
import os
import yaml
import argparse

_parser = argparse.ArgumentParser()
_parser.add_argument("-c", "--config", help="path to yaml configuration file", type=str)

args = _parser.parse_args()

if not args:
    print("no args")

f = open(args.config)

_conf = yaml.safe_load(f)

DB_PASS = _conf['db-pass']
DB_USER = _conf['db-user']
KEY = _conf['sign-key']

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(module)s: %(message)s",
    level="INFO"
)

logging.info("Creating flask app")
app = Flask(__name__, static_url_path='')
app.debug = True

#TODO: make key perm to survive restarts
#signer = TimestampSigner(base64.b64encode(os.urandom(32)))
signer = TimestampSigner(KEY)

logging.info("Loading views")
import banking.views

