from database import query_db
from flask import session

def isAdmin():
	if 'name' not in session:
		return False
	result = query_db("SELECT admin FROM users WHERE username=?;", (session['name'],))
	return result[0][0] == 1
