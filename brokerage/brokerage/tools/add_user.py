
import yaml
import argparse
from brokerage.db import DB, User #, Stock, BrokerageDeal

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--name", type=str)
parser.add_argument("-p", "--pw", type=str)
parser.add_argument("-a", "--admin", type=str)
parser.add_argument("-b", "--balance", type=str)

args, unknown = parser.parse_known_args()

name = args.name
pw = args.pw
admin = True if (args.admin.lower())[0] == 't' else False
balance = float(args.balance)


# does the use exist
user = User.query.filter_by(username=name).first()

if user:
    print("user found, updating password")
    user.update_pass(pw)
else:
    print("creating new user")
    user = User(name, pw, balance, admin)
    DB.session.add(user)
    DB.session.flush()
    DB.session.refresh(user)



DB.session.commit()



