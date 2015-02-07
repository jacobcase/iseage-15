
import yaml
import argparse
from brokerage.db import DB User #, Stock, BrokerageDeal

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--name", type=str)
parser.add_argument("-p", "--pw", type=str)
parser.add_argument("-a", "--admin", type=st)

args, unknown = parser.parse_known_args()

name = args.name
pw = args.pw
admin = (toLower(args.admin)[0] == 't')

# does the use exist
user = User.query.filter_by(username=name).first()
if user:
    print("user found, updating password")
    user.update_pass(pw)
else:
    print("creating new user")
    user = User(name, pw, admin)
    DB.session.add(user)
    DB.session.flush()
    DB.session.refresh(user)
    trans = Transaction(user.id, "initial", Transaction.CREDIT, 0, 0)
    DB.session.add(trans)
    DB.session.commit()


DB.session.commit()



