from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from passlib.hash import sha256_crypt
import os
from banking import app
from datetime import datetime

#   TODO: configure mysql

app.config['SECRET_KEY'] = "todo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rootpass@localhost:3306/banking'

DB = SQLAlchemy(app)

class User(DB.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80)), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = sha256_crypt.encrypt(password)

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password)

    def isAdmin(self):
        return self.username == "ADMINISTRATOR"


class Transaction(DB.Model):
    DEBIT = True
    CREDIT = False

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    transaction = db.Column(db.String(80))
    trans_type = db.Column(db.Boolean)
    amount = db.Column(db.Integer)
    balance = db.Column(db.Integer)
    date = db.Column(db.Date)

    def __init__(self, user_id, transaction, trans_type, amount, balance):
        self.user_id = user_id
        self.transaction = transaction
        self.amount = amount
        self.balance = balance
        self.trans_type = trans_type
        self.date = datetime.utcnow()



