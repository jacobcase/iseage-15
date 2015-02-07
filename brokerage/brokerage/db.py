from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import os
from brokerage import app, DB_PASS, DB_USER
from datetime import datetime


app.config['SECRET_KEY'] = "todo"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DB_USER + ":" + DB_PASS + '@localhost:3306/brokerage'

DB = SQLAlchemy(app)


class User(DB.Model):
	id = DB.Column(DB.Integer, primary_key=True)
	username = DB.Column(DB.String(80), unique=True)
	password = DB.Column(DB.String(255))
	balance = DB.Column(DB.Numeric, asDecimal=True)
	admin = DB.Column(DB.Boolean)

	def __init__(self, username, password, balance, admin):
		self.username = username
		self.password = sha256_crypt.encrypt(password)
		self.admin = admin

	def verify_pass(self, password):
		return sha256_crypt.verify(password, self.password)

	def isAdmin(self):
		return self.admin

	def update_pass(self, password):
		self.password = sha256_crypt.encrypt(password)

	def update_balance(self, balance):
		self.balance = balance

	def update_admin(self, admin):
		self.admin = admin


class StockHolder(DB.Model):
	id = DB.Column(DB.Integer, primary_key=True)
	user_id = DB.Column(DB.Integer) 
	stock_id = DB.Column(DB.Integer)
	ownings = DB.Column(DB.Integer)

	def __init__(self, user_id, stock_id, ownings):
		self.user_id = user_id
		self.stock_id = stock_id
		self.ownings = ownings

	def update_amount(self, ownings):
		self.ownings = ownings
	

class Stock(DB.Model):
	id = DB.Column(DB.Integer, primary_key=True)
	name = DB.Column(DB.String(80), unique=True)
	symbol = DB.Column(DB.String(4), unique=True)
	price = DB.Column(DB.Numeric(), asDecimal=True)

	def __init__(self, name, symbol, price):
		self.name = name
		self.symbol = symbol
		self.price = price

	def update_name(self, name):
		self.name = name

	def update_symbol(self, symbol):
		self.symbol = symbol

	def update_price(self, price):
		self.price = price
		
DB.create_all()

