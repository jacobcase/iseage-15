from flask import render_template, request, session, url_for, redirect, session, make_response
from itsdangerous import TimestampSigner, SignatureExpired
from banking import app, signer
from banking.db import DB, User, Transaction
from banking.utils import *
import base64
import os.path
import pdb

SESSION_AGE = 600

#   The key will be different every time the web server is
#   restarted, this may be unwanted but the server shouldn't crash since
#   it catches exceptions and just fails at one request


INVALID_SESSION = ("Your session is invalid or has expired from inactivity, please log in again", 403)

def forbidden():
    return ("Forbidden!", 403)


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cgi-bin/actions/create-user')
def create_user():
    if not is_admin():
        return forbidden()

    name = request.args.get("name")
    password = request.args.get("password")

    user = User(name, password)
    DB.session.add(user)
    DB.session.flush()
    DB.session.refresh(user)
    initial_trans = Transaction(user.id, "initial", Transaction.CREDIT, 0, 0)
    DB.session.add(initial_trans)
    DB.session.commit()

    res = make_response(redirect(url_for('show_user', user_name=user)))
    res.headers['Content-type'] = 'text/plain'
    res.data = "New user " + name + " created!\n"
    return res 

@app.route('/cgi-bin/actions/delete-user')
def delete_user():
    if not is_admin():
        return forbidden()

    search_user = request.args.get("user_name")
    try:
        user = get_db_user(search_user)
    except UserNotFoundError:
        return plain_response(("User " + search_user + " not found!i\n", 404))

    user_trans = Transaction.query.filter_by(user_id=user.id)
    for trans in user_trans:
        DB.session.delete(trans)

    DB.session.delete(user)
    DB.session.commit()
    return plain_response("User " + search_user + " deleted!")


@app.route('/cgi-bin/actions/find-user')
def find_user():
    """ requires admin """
    if not is_admin():
        return forbidden()
    
    try:
        user = get_db_user(user_name=request.args.get('user_name'))
    except UserNotFoundError:
        return (app.send_static_file('user-not-found.html'), 404)

    balance = get_balance(user)

    return plain_response(str(balance))


@app.route('/cgi-bin/actions/get-access-token', methods=['GET', 'POST'])
def get_access_token():
    pdb.set_trace()
    if request.method == 'POST':
        user = request.form.get('user_name')
        password = request.form.get('password')
    else:
        user = request.args.get('user_name')
        password = request.args.get('password')
    try:
        user = get_db_user(user_name=user)
    except UserNotFoundError:
        return plain_response("User not into existing\n")

    if not user.verify_pass(password):
        return plain_response(redirect(url_for('landing')), data="Wrong!\n")

    session['access_token'] = signer.sign(user.username)
    return plain_response(redirect(url_for('landing')), data=(b"access_token=" + session['access_token']))

@app.route('/cgi-bin/actions/get-admin-access-token')
def get_admin_token():
    pdb.set_trace()
    password = request.args.get('password')
    try:
        user = get_db_user(user_name="ADMINISTRATOR")
    except UserNotFoundError:
        return plain_response("User not into existing\n")

    if not user.verify_pass(password):
        return plain_response("Wrong!\n")

    session['access_token'] = signer.sign(user)
    return plain_response("access_token=" + session['access_token'])

@app.route('/cgi-bin/actions/logout')
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route('/cgi-bin/actions/make-deposit')
def make_deposit():
    if not valid_admin():
        return forbidden()
     
    try:
        user = get_db_user(user_name=request.args.get("user_name"))
    except UserNotFoundError:
        user = request.args.get("user_name")
        return plain_response(("User " + str(user) + " does not exist!\n", 404))

    amount = request.args.get('amount')
    try:
        amount = int(amount)
    except Exception:
        return empty_response()

    balance = get_balance(user)
    new_balance = balanc + amount
    trans = Transaction(user.id, "Deposit", Transaction.CREDIT, amount, new_balance)
    DB.session.add(trans)
    DB.session.commit()
    return plain_response(redirect(url_for('show_user'), user_name=user.username), data=("amt " +
        str(new_balance)))


@app.route('/cgi-bin/actions/make-payment')
def make_payment():
    if not is_admin():
        from_user = get_db_user()
    else:
        try:
            from_user = get_db_user(request.args.get('user_name'))
        except UserNotFoundError:
            user = request.args.get('user_name')
            return plain_response(("User " + str(user) + " not found!\n", 404))

    try:
        to_user = get_db_user(request.args.get('other_party'))
    except UserNotFoundError:
        user = request.args.get('other_party')
        return plain_response(("Other party " + str(user) + " not found!\n", 404))

    amount = request.args.get('amount')
    try:
        amount = int(amount)
    except Exception:
        return empty_response()

    from_balance = get_balance(from_user)
    to_balance = get_balance(to_user)
    from_new_balance = from_balance - amount
    to_new_balance = to_balance + amount

    from_transaction = Transaction(from_user.id, to_user.username,  Transaction.DEBIT, amount, from_new_balance)
    to_transaction = Transaction(to_user.id, from_user.username, Transaction.CREDIT, amount, to_new_balance)

    DB.session.add(from_transaction)
    DB.session.add(to_transaction)
    DB.session.commit()

    return plain_response(redirect(url_for("show_user"), user_name=from_user.username), data=("amt "
        + str(from_new_balance)))


@app.route('/cgi-bin/actions/make-withdrawal')
def make_withdrawal():
    if not is_admin():
        return forbidden()

    try:
        user = get_db_user(request.args.get("user_name"))
    except UserNotFoundError:
        user = request.args.get("user_name")
        return plain_response(("User " + str(user) + " does not exist", 404))

    amount = request.args.get('amount')
    try:
        amount = int(amount)
    except Exception:
        return empty_response()

    balance = get_balance(user)
    new_balance = balance - amount
    new_trans = Transaction(user.id, "Withdrawal", Transaction.DEBIT, amount, new_balance)
    DB.session.add(new_trans)
    DB.session.commit()
    return plain_response(redirect(url_for('show_user'), user_name=user.username), data=("amt " +
        str(new_balance)))


@app.route('/cgi-bin/show/landing')
def landing():
    pdb.set_trace()
    try:
        user = get_db_user()
    except (InvalidSessionError, UserNotFoundError):
        return render_template("not-logged-in.html")    
    return render_template("welcome.html", USER_NAME=user.username)


@app.route('/cgi-bin/show/show-user')
def show_user():
    pdb.set_trace()
    try:
        user = get_db_user()
    except InvalidSessionError:
        return forbidden()
    except UserNotFoundError:
        return (render_template("user-not-found.html"), 404)

    try:
        req_user = get_db_user(request.args.get("user_name"))
    except UserNotFoundError:
        return (render_template("user-not-found.html"), 404)

    if not user.isAdmin() and user.id != req_user.id:
        return forbidden()

    transaction_array = []
    transactions = Transaction.query.filter_by(user_id = req_user.id).order_by(desc(Transaction.date)).all()
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

    balance = get_balance(req_user) 

    return render_template("user.html", USER_NAME=req_user, BALANCE=balance, TABLE=transaction_array)
