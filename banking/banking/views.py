from flask import render_template, request, session, url_for, redirect, session, make_response
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
    res.headers['Content-Type'] = 'text/plain'
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

    search_user = request.args.get("user_name")
    result = User.query.filter_by(username=search_user).first()
    if not result:
        return (app.send_static_file('user-not-found.html'), 404)

    res = make_response(str(result.balance))
    res.headers['Content-Type'] = 'text/plain'
    return res


@app.route('/cgi-bin/actions/get-access-token')
def get_access_token():
    password = request.args.get('password')
    user = request.args.get('user_name')
    db_user = User.query.filter_by(username=user).first()
    if not db_user or not db_user.verify_pass(password):
        # TODO: C app prints "Wrong!\n" here with redirect
        return redirect(url_for('landing'))
    session['access_token'] = s.sign(user)
    return redirect(url_for('landing'))

@app.route('/cgi-bin/actions/get-admin-access-token')
def get_admin_token():
    password = request.args.get('password')
    user = "ADMINISTRATOR"
    db_user = User.query.filter_by(username=user).first()
    if not db_user.verify_pass(password):
        return redirect(url_for('landing'))

    session['access_token'] = s.sign(user)

@app.route('/cgi-bin/actions/logout')
def logout():
    # remove users cookie, delete their session from the database
    # all that security stuff
    return redirect(url_for("landing"))

@app.route('/cgi-bin/actions/make-deposit')
def make_deposit():
    pass

@app.route('/cgi-bin/actions/make-payment')
def make_payment():
    pass

@app.route('/cgi-bin/actions/make-withdrawal')
def make_withdrawal():
    pass

@app.route('/cgi-bin/show/landing')
def landing():
    user = "cdc" # replace
    #check the auth
    authenticated = True
    if not authenticated:
        return render_template("not-logged-in.html")
    else:
        return render_template("welcome.html", USER_NAME=user)


@app.route('/cgi-bin/show/show-user')
def show_user():
    if not valid_session():
        return forbidden()

    balance = "100"
    tansactions = []
    authenticated = True

    if not authenticated:
        return ("Status: 403\nForbidden!", 403)
    
    if not user:
        return render_template("user-not-found.html")

    return render_template("user.html", USER_NAME=user, BALANCE=balance)
