
import yaml
import argparse
from banking.db import DB, User

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--name", type=str)
parser.add_argument("-p", "--pw", type=str)

args, unknown = parser.parse_known_args()

name = args.name
pw = args.pw

# does the use exist
user = User.query.filter_by(username=name).first()
if user:
    print("user found, updating password")
    user.update_pass(pw)
else:
    print("creating new user")
    user = User(name, pw)
    DB.session.add(user)


DB.session.commit()



