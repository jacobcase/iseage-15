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
    pass

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
    pass

@app.route('/cgi-bin/show/show-user')
def show_user():
    pass
