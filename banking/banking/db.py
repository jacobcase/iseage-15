from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from passlib.hash import sha256_crypt
import os
from banking import app

#   TODO: configure mysql

app.config['SECRET_KEY'] = "todo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

DB = SQLAlchemy(app)

class User(DB.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80)), unique=True)
    password = db.Column(db.String(255))
    balance = db.Column(db.Float)

    def __init__(self, username, password, balance=0):
        self.username = username
        self.password = sha256_crypt.encrypt(password)
        self.balance = balance

    def verify_pass(self, password):
        return sha256_crypt.verify(password, self.password)

    def isAdmin(self):
        return self.username == "ADMINISTRATOR"


