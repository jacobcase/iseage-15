from flask import session, Response, make_response
from brokerage import signer
from brokerage.db import User, StockHolder, Stock
from itsdangerous import BadSignature

class UserNotFoundError(Exception):
    def __init__(self, message):
        super(UserNotFoundError, self).__init__(message)

class InvalidSessionError(Exception):
    def __init__(self, message):
        super(InvalidSessionError, self).__init__(message)


def authenticate(username, password):
    try:
        user = get_db_user(username)
    except UserNotFoundError:
        return None

    if not user.verify_pass(password):
        return None

    return user

def authorize():
    try:
        user = get_db_user()
    except InvalidSessionError:
        return None

    return user
        

def get_db_user(user_name=None):
    if not user_name:
        token = session.get('name')
        if not token:
            raise InvalidSessionError("Access token not found")
        try:
            user = signer.unsign(token)
        except BadSignature:
            raise InvalidSessionError("Bad cookie signature")

    else:
        user = user_name.strip()

    db_user = User.query.filter_by(username=user).first()
    if not db_user:
        raise UserNotFoundError("User not found in database")
    else:
        return db_user
