from database import query_db
from helper import isAdmin
import logging
from logging import FileHandler

from flask import Flask, render_template, request, url_for, session, redirect

app = Flask(__name__)
app.config['Debug'] = True
app.secret_key = "cdc"

@app.route("/")
def home():
	return home_page()

@app.route("/login", methods=['GET', 'POST'])
def login():
	if 'name' in session:
		if(isAdmin()):
			return redirect(url_for("admin"))
		else:
			return redirect(url_for("home"))
	if request.method == 'POST':
		session['name'] = request.form['username']
		if (not isAdmin()):
			return redirect(url_for("home"))
		else:
			return redirect(url_for("admin"))
	else:
		return render_template('login.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if request.method == "POST":
		if 'username' in request.form:
			username = request.form['username']
			password = request.form['password']
			balance = request.form['balance']
			admin = 'admin' in request.form
			result = query_db("SELECT uid FROM users ORDER BY uid DESC LIMIT 1;")
			uid = result[0][0] + 1
			query_db("INSERT INTO users (uid, username, password, balance, admin) VALUES (?, ?, ?, ?, ?);", (uid, username, password, balance, admin))
		elif 'company' in request.form:
			name = request.form['company']
			symbol = request.form['symbol']
			price = request.form['price']
			result = query_db("SELECT stock_id FROM prices ORDER BY stock_id DESC LIMIT 1;")
			stock_id = result[0][0] + 1
			query_db("INSERT INTO prices(stock_id, stock_price, stock_symbol, stock_name) VALUES (?, ?, ?, ?);", (stock_id, price, symbol, name))
	result = query_db("SELECT * FROM users;")
	stocks = query_db("SELECT * FROM prices;")
	return render_template('admin.html', users = result, stocks=stocks, admin=isAdmin())

@app.route("/user", methods=['GET', 'POST'])
def user():
	name = request.args.get('name', '')
	if request.method == 'POST':
		if 'admin' in request.form:
			admin = False
			if request.form['admin'] == 'on':
				admin = True
			query_db("UPDATE users SET admin=? WHERE username=?;", (admin, name))
		elif 'action' in request.form:
			userinfo = query_db("SELECT * FROM users where username = ?;", (name,))
			query_db("DELETE FROM users WHERE uid=?", (userinfo[0][0],))
			query_db("DELETE FROM stockholders WHERE uid=?", (userinfo[0][0],))
			return redirect(url_for("admin"))
		else:
			password = request.form['password']
			query_db("UPDATE users SET password=? WHERE username=?", (password, name))

	user_info = query_db("SELECT * FROM users where username = ?;", (name,))
	stock_holdings = query_db("SELECT stock_symbol, stock_price, stock_name, amount FROM prices, stockholders WHERE  stockholders.uid = ? AND stockholders.stock_id = prices.stock_id;", (user_info[0][0],))
	if stock_holdings == None:
		stock_holdings = []
	return render_template("user_home.html", user_info=user_info, stock_holdings=stock_holdings, admin=isAdmin())

@app.route("/home", methods=['GET', 'POST'])
def home_page():
	if 'name' not in session:
		return redirect(url_for("login"))
	name = session['name']
	if request.method == 'POST':
		if request.form['action'] == 'buy':
			number = int(request.form['number'])
			symbol = request.form['symbol']
			stock_info = query_db("SELECT stock_price, stock_id FROM prices WHERE stock_symbol = ?", (symbol,));
			uinfo = query_db("SELECT balance, uid FROM users WHERE username= ?", (name,))
			ownings = query_db("SELECT amount FROM stockholders WHERE stock_id=? AND uid=?;", (stock_info[0][1], uinfo[0][1]))
			amount = number;
			if ownings != None:
				amount += ownings[0][0]
			cost = stock_info[0][0]
			total = cost*number
			balance = uinfo[0][0]
			balance = balance - cost*number
			query_db("UPDATE users SET balance=? WHERE username=?", (balance, name))
			if ownings != None:
				query_db("UPDATE stockholders SET amount=? WHERE uid=? AND stock_id=?;", (amount, uinfo[0][1], stock_info[0][1]))
			else:
				query_db("INSERT INTO stockholders(stock_id, uid, amount) VALUES (?, ?, ?);", (stock_info[0][1], uinfo[0][1], amount))
		elif request.form['action'] == 'sell':
			number = int(request.form['number2'])
			symbol = request.form['symbol2']
			uinfo = query_db("SELECT balance, uid FROM users WHERE username= ?", (name,))
			stock_info = query_db("SELECT stock_price, stock_id FROM prices WHERE stock_symbol = ?", (symbol,));
			ownings = query_db("SELECT amount FROM stockholders WHERE stock_id=? AND uid=?;", (stock_info[0][1], uinfo[0][1]))
			amount = ownings[0][0] - number;
			cost = stock_info[0][0];
			total = cost*number;
			balance = uinfo[0][0]
			balance = balance + cost*number
			query_db("UPDATE users SET balance=? WHERE username=?", (balance, name))
			query_db("UPDATE stockholders SET amount=? WHERE uid=? AND stock_id=?;", (amount, uinfo[0][1], stock_info[0][1]))
	user_info = query_db("SELECT * FROM users where username = ?;", (name,))
	stock_holdings = query_db("SELECT stock_symbol, stock_price, stock_name, amount FROM prices, stockholders WHERE  stockholders.uid = ? AND stockholders.stock_id = prices.stock_id;", (user_info[0][0],))
	if stock_holdings == None:
		stock_holdings = []
	stocks = query_db("SELECT * FROM prices;")
	a = render_template("home.html", user_info=user_info, stock_holdings=stock_holdings, stocks=stocks, admin=isAdmin())
	return a

@app.route("/stock", methods=['GET', 'POST'])
def stock_edit():
	name = request.args.get('name', '')
	if request.method == 'POST':
		price = request.form['price']
		new_name = request.form['name']
		symbol = request.form['symbol']
		query_db("UPDATE prices SET stock_price=? WHERE stock_name=?;", (price, name))
		query_db("UPDATE prices SET stock_symbol=? WHERE stock_name=?", (symbol, name))
		query_db("UPDATE prices SET stock_name=? WHERE stock_name=?", (new_name, name))
		name = new_name
	info = query_db("SELECT * FROM prices WHERE stock_name = ?", (name,))
	return render_template("stock.html", stock=info[0], admin=isAdmin())

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
