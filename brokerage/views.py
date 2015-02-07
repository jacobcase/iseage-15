from flask import Flask, render_template, request, url_for, session, redirect
from itsdangerous import TimestampSigner, SignatureExpired

#from banking import app, signer

from database import query_db
from utils import *
from db import DB, User, StockHolder, Stock

import logging
from logging import FileHandler

import base64
import os.path


app = Flask(__name__)
app.config['Debug'] = True
app.secret_key = "cdc"

@app.route("/")
def home():
	return home_page()

@app.route("/login", methods=['GET', 'POST'])
def login():
	if 'name' in session:
		user = authorize()
			
	if request.method == 'POST':
        	username = request.form.get('username')
        	password = request.form.get('password')
		user = authenticate(username, password)
		session['name'] = signer.sign(user.username)

	if(user):	
		if(user.isAdmin):						//Fix this
			return redirect(url_for("admin"))
		else:
			return redirect(url_for("home"))

	return render_template('login.html')  	

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	user = authorize()
	if(not user or not user.isAdmin):
		return redirect(url_for("login"))

	if request.method == "POST":
		if 'username' in request.form:
			username = request.form['username']
			password = request.form['password']
			balance = request.form['balance']
			admin = 'admin' in request.form
			new_user = User(username,password,balance,admin)
			DB.session.add(user)

		elif 'company' in request.form:
			name = request.form['company']
			symbol = request.form['symbol']
			price = request.form['price']
			new_stock = Stock(name, symbol, price)

	result = query_db("SELECT * FROM users;")
	stocks = query_db("SELECT * FROM prices;")
	return render_template('admin.html', users = result, stocks=stocks, admin=isAdmin())

@app.route("/user", methods=['GET', 'POST'])
def user():
	user = authorize()
	if not user or not user.isAdmin:
		return redirect(url_for("login"))

	name = request.args.get('name', '')
	mod_user = get_db_user(name)
	if request.method == 'POST':
		if 'admin' in request.form:
			admin = False
			if request.form['admin'] == 'on':
				admin = True
			mod_user.update_admin(admin)

		elif 'action' in request.form:
			stockholds = StockHolder.query.filter_by(user_id)
			for stockhold in stockholds:
				DB.session.delete(stockhold)
			DB.session.delete(mod_user)
			return redirect(url_for("admin"))
		else:
			password = request.form['password']
			mod_user.update_pass(password)
	
	user_info = query_db("SELECT * FROM users where username = ?;", (name,))
	stock_holdings = query_db("SELECT stock_symbol, stock_price, stock_name, amount FROM prices, stockholders WHERE  stockholders.uid = ? AND stockholders.stock_id = prices.stock_id;", (user_info[0][0],))
	if stock_holdings == None:
		stock_holdings = []
	return render_template("user_home.html", user_info=user_info, stock_holdings=stock_holdings, admin=isAdmin())

@app.route("/home", methods=['GET', 'POST'])
def home_page():
	user = authorize()
	if not user:
		return redirect(url_for("login"))

	name = user.username

	if request.method == 'POST':
		if request.form['action'] == 'buy':
			number = int(request.form['number'])
			stock_symb = request.form['symbol']
			stock = Stock.query.filter_by(symbol=stock_symb).first()
			stockhold = StockHolder.query.filter_by(stock_id=stock.id,user_id=user.id).first()

			amount = number;
			cost = stock.price
			total = cost*number
			balance = user.balance
			balance = balance - cost*number
			user.update_balance(balance)

			if stockhold:
				stockhold.update_ownings(amount)
			else:
				stockhold = StockHolder(user.id, stock.id, amount)

		elif request.form['action'] == 'sell':
			number = int(request.form['number2'])
			stock_symb = request.form['symbol2']
			uinfo = query_db("SELECT balance, uid FROM users WHERE username= ?", (name,))
			stock = Stock.query.filter_by(symbol=stock_symb).first
			shockhold = StockHolder.query.filter_by(stock_id=stock.id,user_id=user.id).first()
			amount = stockhold.ownings - number;
			total = stock.price*number;
			user.update_balance(user.balance + total)
			stockhold.update_ownings(amount)

	user_info = query_db("SELECT * FROM users where username = ?;", (user.name,))
	stock_holdings = query_db("SELECT stock_symbol, stock_price, stock_name, amount FROM prices, stockholders WHERE  stockholders.uid = ? AND stockholders.stock_id = prices.stock_id;", (stockhold.user_id,))

	if stock_holdings == None:
		stock_holdings = []

	stocks = query_db("SELECT * FROM prices;")
	a = render_template("home.html", user_info=user_info, stock_holdings=stock_holdings, stocks=stocks, admin=user.isAdmin())
	return a

@app.route("/stock", methods=['GET', 'POST'])
def stock_edit():
	user = authorize()
	if not user:
		return redirect(url_for("login"))

	stock_name = request.args.get('name', '')
	if request.method == 'POST':
		price = request.form['price']
		new_name = request.form['name']
		symbol = request.form['symbol']
		stock = Stock.query.filter_by(name=stock_name).first()
		stock.update_name(new_name)
		stock.update_symbol(symbol)
		stock.update_price(price)
	return render_template("stock.html", stock.price, admin=user.isAdmin())

@app.route("/logout", methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.Debug = True
	app.Testing = True
	file_handler = FileHandler("/var/www/brokerage/log")
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.run()
