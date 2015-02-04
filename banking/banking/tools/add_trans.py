
import yaml
import argparse
from banking.db import DB, User, Transaction
import pdb
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--transaction", type=str)

args, unknown = parser.parse_known_args()

trans = args.transaction.split()

t_type = trans[0]
t_amount = int(trans[1])
t_user = trans[2]

user = User.query.filter_by(username=t_user).first()
if not user:
    print("user not found")
    sys.exit(2)

prev = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.id.desc()).first()

if t_type == "deposit":
    balance = prev.balance + t_amount
    t = Transaction(user.id, "Deposit", Transaction.CREDIT, t_amount, balance)
    DB.session.add(t)
elif t_type == "withdrawal":
    balance = prev.balance - t_amount
    t = Transaction(user.id, "Withdrawal", Transaction.DEBIT, t_amount, balance)
    DB.session.add(t)

elif t_type == "transfer":
    other_user = User.query.filter_by(username=trans[3]).first()
    if not other_user:
        print("Other user does not exist")
        sys.exit(2)

    prev_other = Transaction.query.filter_by(user_id=other_user.id).order_by(Transaction.id.desc()).first()
    
    balance = prev.balance - t_amount
    other_balance = prev_other.balance + t_amount
    t = Transaction(user.id, other_user.username, Transaction.DEBIT, t_amount, balance)
    t2 = Transaction(other_user.id, user.username, Transaction.CREDIT, t_amount, other_balance)

    DB.session.add(t)
    DB.session.add(t2) 


DB.session.commit()
