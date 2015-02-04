
import yaml
import argparse
from banking.db import DB, User, Transaction
import pdb

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--transaction", type=str)

args, unknown = parser.parse_known_args()

trans = args.transaction.split()

t_type = trans[0]
t_amount = int(trans[1])
t_user = trans[2]
t_id = int(trans[len(trans) - 1])

res = Transaction.query.filter_by(id=t_id).first()
if res:
    print("key already exists")
    return

user = User.query.filter_by(username=t_user).first()
if not user:
    print("user not found")
    return

prev = Transaction.query.filter_by(user.id).filter_by(id < t_id).order_by(Transaction.id).last()


if t_type == "deposit":
    balance = prev.balance + t_amount
    t = Transaction(user.id, "Deposit", Transaction.CREDIT, t_amount, balance, key=t_id)
    DB.session.add(t)
elif t_type == "withdrawal":
    balance = prev.balance - t_amount
    t = Transaction(user.id, "Withdrawal", Transaction.DEBIT, t_amount, balance, key=t_id)
    DB.session.add(t)

elif t_type == "transfer":
    other_user = User.query.filter_by(username=trans[3]).first()
    if not other_user:
        print("Other user does not exist")
        return

    prev_other = Transaction.query.filter_by(other_user.id).filter_by(id < t_id).orger_by(Transaction.id).last()
    
    balance = prev.balance - t_amount
    other_balance = prev_other + t_amount
    t = Transaction(user.id, other_user.username, Transaction.DEBIT, t_amount, balance, key=t_id)
    t2 = Transaction(other_user.id, user.username, Transaction.CREDIT, t_amount, other_balance, key=t_id + 1)

    DB.session.add(t)
    DB.session.add(t2) 


DB.session.commit()
