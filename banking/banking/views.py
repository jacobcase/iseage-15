from flask import render_template, request, session, url_for, redirect

from banking import app
import os.path

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cgi-bin/actions/create-user')
def create_user():
    pass

@app.route('/cgi-bin/actions/delete-user')
def delete_user():
    pass

@app.route('/cgi-bin/actions/find-user')
def find_user():
    pass

@app.route('/cgi-bin/actions/get-access-token')
def get_access_token():
    pass

@app.route('/cgi-bin/actions/get-admin-access-token')
def get_admin_token():
    pass

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
    user = "cdc"
    balance = "100"
    tansactions = []
    authenticated = True

    if not authenticated:
        return ("Status: 403\nForbidden!", 403)
    
    if not user:
        return render_template("user-not-found.html")

    return render_template("user.html", USER_NAME=user, BALANCE=balance)
