
import yaml
import argparse
from banking.db import DB, User, Transaction

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--flag", type=str)

args, unknown = parser.parse_known_args()

flag = args.flag

user = User.query.filter_by(username="Charlie").first()

trans = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.id).first()

trans.flag = flag

DB.session.commit()
