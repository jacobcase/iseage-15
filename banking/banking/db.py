from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from passlib.hash import sha256_crypt
import os
from banking import app, DB_PASS, DB_USER
from datetime import datetime


#   TODO: configure mysql

app.config['SECRET_KEY'] = "todo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DB_USER + ":" + DB_PASS + '@localhost:3306/banking'

DB = SQLAlchemy(app)

class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True)
    password = DB.Column(DB.String(255))

    def __init__(self, username, password):
        self.username = username.strip()
        self.password = sha256_crypt.encrypt(password)

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password)

    def isAdmin(self):
        return self.username == "ADMINISTRATOR"

    def update_pass(self, password):
        self.password = sha256_crypt.encrypt(password)

class Transaction(DB.Model):
    DEBIT = True
    CREDIT = False

    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer)
    transaction = DB.Column(DB.String(80))
    trans_type = DB.Column(DB.Boolean)
    amount = DB.Column(DB.Integer)
    balance = DB.Column(DB.Integer)
    flag = DB.Column(DB.String(512))

    def __init__(self, user_id, transaction, trans_type, amount, balance, key=None):
        if key:
            self.id = key

        self.user_id = user_id
        self.transaction = transaction
        self.amount = amount
        self.balance = balance
        self.trans_type = trans_type


DB.create_all()
