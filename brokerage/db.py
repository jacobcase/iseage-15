from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import os


app.config['SECRET_KEY'] = "todo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DB_USER + ":" + DB_PASS + '@localhost:3306/banking'

DB = SQLAlchemy(app)


class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True)
    password = DB.Column(DB.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = sha256_crypt.encrypt(password)

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password)

    def isAdmin(self):
        return self.username == "ADMINISTRATOR"

    def update_pass(self, password):
        self.password = sha256_crypt.encrypt(password)


class Stock(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name
    price


class BrokerageDeal(DB.Model):
    BUY = True
    SELL = False

    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer)

    deal_type = DB.Column(DB.Boolean)
	

