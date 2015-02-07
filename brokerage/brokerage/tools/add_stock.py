
import yaml
import argparse
from brokerage.db import DB User, Stock, StockHolder

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--name", type=str)
parser.add_argument("-p", "--symbol", type=str)
parser.add_argument("-a", "--price", type=st)

args, unknown = parser.parse_known_args()

name = args.name
pw = args.pw
admin = (toLower(args.admin)[0] == 't')

# does the use exist
stock = Stock.query.filter_by(name=name).first()
if stock:
    print("Stock found, updating password")
    stock.update_price(price)
    stock.update_symbol(symbol)
else:
    print("creating new user")
    stock = Stock(name, symbol, price)
    DB.session.add(stock)
    DB.session.flush()
    DB.session.refresh(stock)

DB.session.commit()



