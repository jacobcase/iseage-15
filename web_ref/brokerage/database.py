from flask import g
import sqlite3

DATABASE = "/var/www/brokerage/db/brokerage.db"


def connect_to_database():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

def query_db(query, args=(), one=False):
    db=get_db()
    con = db.cursor().execute(query, args)
    result = con.fetchall()
    db.commit()
    return result if result else None


