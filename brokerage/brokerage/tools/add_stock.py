
import yaml
import argparse
from brokerage.db import DB, User, Stock, StockHolder

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", type=str)
parser.add_argument("-s", "--symbol", type=str)
parser.add_argument("-p", "--price", type=str)

args, unknown = parser.parse_known_args()

name = args.name
sym = args.symbol
price = float(args.price)

# does the use exist
stock = Stock.query.filter_by(name=name).first()
if stock:
    print("Stock found, updating price")
    stock.update_price(price)
    stock.update_symbol(sym)
else:
    print("creating new stock")
    stock = Stock(name, sym, price)
    DB.session.add(stock)
    DB.session.flush()
    DB.session.refresh(stock)

DB.session.commit()



