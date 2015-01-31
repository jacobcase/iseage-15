from flask import render_template, request, session, url_for, redirect, session, make_response, set_cookie
from itsdangerous import TimestampSigner, SignatureExpired
from banking import app
from banking.db import DB, User
import base64
import os.path

SESSION_AGE = 600

#   The key will be different every time the web server is
#   restarted, this may be unwanted but the server shouldn't crash since
#   it catches exceptions and just fails at one request

s = TimestampSigner(base64.b64encode(os.urandom(32)))

INVALID_SESSION = ("Your session is invalid or has expired from inactivity, please log in again", 403)

def forbidden():
    return ("Forbidden!", 403)

def valid_admin():

def valid_session():
    # For now just validate the token, this is useful if we decide to
    # do server side sessions
    token = session.get('access_token')
    if not token:
        return False, redirect(url_for('landing'))
    s.validate(token)

def allowed_access(name):
    if valid_admin():
        return True

    token = session.get('access_token')
    if not token:
        return False

    token_name = s.unsign(token)
    if token_name != name:
        return False

    return True

def refresh_session():
    token = session.get('access_token')
    user = s.unsign(token)
    token = s.sign(token)
    session['access_token'] = token

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cgi-bin/actions/create-user')
def create_user():
    if not valid_admin():
        return forbidden()

    name = request.args.get("name")
    password = request.args.get("password")

    user = User(name, password)
    DB.session.add(user)
    DB.session.commit()

    res = make_response(redirect(url_for('show_user', user_name=user)))
    res.headers['Content-type'] = 'text/plain'
    res.data = "New user " + name + " created!\n"
    return res 

@app.route('/cgi-bin/actions/delete-user')
def delete_user():
    if not valid_admin():
        return forbidden()

    # TODO: validate
    search_user = request.args.get("user_name")
    db_user = User.query.filter_by(username=search_user)
    if not db_user:
        return ("User " + search_user + " not found!", 404)

    DB.session.delete(db_user)
    DB.session.commit()
    return "User " + search_user + " deleted!"

@app.route('/cgi-bin/actions/find-user')
def find_user():
    """ requires admin """
    if not valid_admin():
        return forbidden()

    # TODO: validate
    search_user = request.args.get("user_name")
    result = User.query.filter_by(username=search_user).first()
    if not result:
        return (app.send_static_file('user-not-found.html'), 404)

    res = make_response(str(result.balance))
    res.headers['Content-type'] = 'text/plain'
    return res


@app.route('/cgi-bin/actions/get-access-token')
def get_access_token():
    password = request.args.get('password')
    user = request.args.get('user_name')
    db_user = User.query.filter_by(username=user).first()
    if not db_user:
        res = make_response("User not into existing\n")
        res.headers['Content-type'] = 'text/plain'
        return res

    if not db_user.verify_pass(password):
        res = make_response(redirect(url_for('landing')))
        res.data = "Wrong!\n"
        res.headers['Content-type'] = 'text/plain'
        return res

    session['access_token'] = s.sign(user)
    res = make_response(redirect(url_for('landing')))
    res.data = "access_token=" + session['access_token']
    res.headers['Content-type'] = 'text/plain'
    return res

@app.route('/cgi-bin/actions/get-admin-access-token')
def get_admin_token():
    password = request.args.get('password')
    user = "ADMINISTRATOR"
    db_user = User.query.filter_by(username=user).first()
    if not db_user:
        res = make_request("User not into existing\n")
        res.headers['Content-type'] = 'text/plain'
        return res
    if not db_user.verify_pass(password):
        res = make_request("Wrong!\n")
        res.headers['Content-type'] = 'text/plain'
        return res

    session['access_token'] = s.sign(user)
    res = make_response("access_token=" + session['access_token'])
    res.headers['Content-type'] = 'text/plain'
    return res

@app.route('/cgi-bin/actions/logout')
def logout():
    res = make_response()
    return redirect(url_for("landing"))

@app.route('/cgi-bin/actions/make-deposit')
def make_deposit():
    if not valid_admin():
        return forbidden()
     
    search_user = request.args.get("user_name")
    DBuser = User.query.filter_by(username=search_user).first()
    if not DBuser:
        res = make_response("User " + search_user + " does not exist!\n", 404)
        res.headers['Content-type'] = 'text/plain'
        return res
    amount = request.args.get('amount')
    try:
        amount = int(amount)
    except Exception:
        pass

    new_balance = DBuser.balance + amount
    trans = Transaction(DBuser.id, Transaction.DEPOSIT, amount, new_balance)
    DB.session.add(trans)
    DB.session.commit()
    res = make_response(redirect("show_user"))



@app.route('/cgi-bin/actions/make-payment')
def make_payment():
    session_user = get_session_user()

    if session_user == "ADMINISTRATOR":
        from_user = request.args.get('user_name')
    else:
        from_user = session_user

    to_user = request.args.get("other_party")
    DBfrom_user = User.query.filter_by(username=from_user).one()
    DBto_user = User.query.filter_by(username=to_user).one()
    if not DBfrom_user:
        res = make_response("User " + from_user + " not found!\n", 404)
        res.headers['Content-type'] = 'text/plain'
        return res

    if not DBto_user:
        res = make_response("Other party " + to_user + " not found!\n", 404)
        res.headers['Content-type'] = 'text/plain'
        return res

    amount = request.args.get('amount')
    from_user_last = Transaction.query.filter_by(user_id=DBfrom_user.id).order_by(desc(Transaction.date)).last()
    to_user_last = Transaction.query.filter_by(user_id=DBto_user.id).order_by(desc(Transaction.date)).last()
    from_new_amount = from_user_last.balance - amount
    to_user_amount = to_user_last.balance + amount

    from_transaction = Transaction(from_user.id, 


@app.route('/cgi-bin/actions/make-withdrawal')
def make_withdrawal():
    if not session_admin():
        return forbidden()
    user = request.args.get("user_name")

    DBuser = User.query.filter_by(username=user).first()
    if not DBuser:
        res = make_response(("User " + user + " does not exist", 404))
        res.headers['Content-type'] = 'text/plain'
        return res
    amount = request.args.get('amount')
    last_trans = Transaction.query.filter_by(user_id=DBuser.id).order_by(desc(Transaction.date)).last()
    new_amount = last_trans.balance - amount
    new_trans = Transaction(DBuser.id, 


@app.route('/cgi-bin/show/landing')
def landing():
    user = get_session_user()
    if not user:
        return render_template("not-logged-in.html")    
    else:
        return render_template("welcome.html", USER_NAME=user)


@app.route('/cgi-bin/show/show-user')
def show_user():
    user = get_session_user()
    if not user:
        return forbidden()

    req_user = request.args.get("user_name")
    if not req_user:
        return forbidden()

    if not session_admin() and user != req_user:
        return forbidden()

    
    DBuser = User.query.filter_by(username=req_user).first()
    if not DBuser:
        return (render_template("user-not-found.html"), 404)

    transaction_array = []
    transactions = Transaction.query.filter_by(user_id = DBuser.id).order_by(desc(Transaction.date)).all()
    for transaction in transactions:
        tmp = []
        tmp.append(transaction.transaction)
        if transaction.trans_type == Transaction.DEBIT:
            tmp.append(transaction.amount)
            tmp.append(None)
        else:
            tmp.append(None)
            tmp.append(transaction.amount)

        tmp.append(transaction.balance)
        transaction_array.append(tmp)

    balance = transaction_array[len(transaction_array) - 1][3] 

    return render_template("user.html", USER_NAME=req_user, BALANCE=balance, TABLE=transaction_array)
