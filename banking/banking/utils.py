from banking import signer
from flask import session, Response, make_response
from banking.db import User, Transaction, DB
from itsdangerous import BadSignature
import logging

class UserNotFoundError(Exception):
    def __init__(self, message):
        super(UserNotFoundError, self).__init__(message)

class InvalidSessionError(Exception):
    def __init__(self, message):
        super(InvalidSessionError, self).__init__(message)


def get_db_user(user_name=None):
    if not user_name:
        token = session.get('access_token')
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

def get_balance(user):
    trans = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.id.desc()).first()
    return trans.balance

def is_admin(user_name=None):

    try:
        db_user = get_db_user(user_name)
    except UserNotFoundError:
        return False
    except InvalidSessionError:
        return False

    if db_user.username == "ADMINISTRATOR":
        return True
    else:
        return False

def plain_response(response, data=None, code=None):
    if isinstance(response, Response):
        response.headers['Content-type'] = 'text/plain'
        if data:
            response.data = data
        if code:
            response.status_code = code
        return response
    else:
        res = make_response(response)
        res.headers['Content-type'] = 'text/plain'
        if data:
            res.data = data
        if code:
            res.status_code = code
        return res

def empty_response():
    return ('', 204)
