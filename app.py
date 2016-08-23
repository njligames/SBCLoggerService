from flask import request
from flask import Response
from flask import json
import sqlite3
from flask import g
import json
from flask import Flask, jsonify, make_response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

__all__ = ['make_json_app']

def make_json_app(import_name, **kwargs):
	"""
	Creates a JSON-oriented Flask app.

	All error responses that you don't specifically
	manage yourself will have application/json content
	type, and will contain JSON like this (just an example):

	{ "message": "405: Method Not Allowed" }
	"""
	def make_json_error(ex):
		response = jsonify(message=str(ex))
		response.status_code = (ex.code
					if isinstance(ex, HTTPException)
					else 500)
		return response

	app = Flask(import_name, **kwargs)

	for code in default_exceptions.iterkeys():
		app.error_handler_spec[None][code] = make_json_error

	return app

#app = Flask(__name__)
app = make_json_app(__name__)

databasepath = '/usr/data/phidgetdata.db'

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(databasepath)#, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		db.row_factory = dict_factory
	return db

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.errorhandler(404)
def not_found(error=None):
	message = {
		'status': 404,
		'message': 'Not Found: ' + request.url,
	}
	resp = jsonify(message)
	resp.status_code = 404

	return resp

def default(obj):
	"""Default JSON serializer."""
	import calendar, datetime

	if isinstance(obj, datetime.datetime):
		if obj.utcoffset() is not None:
			obj = obj - obj.utcoffset()
		millis = int(
			calendar.timegm(obj.timetuple()) * 1000 +
			obj.microsecond / 1000
		)
		return millis
	raise TypeError('Not sure how to serialize %s' % (obj,))

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


def selectDateRange(table, 
		year_from, month_from, day_from, hour_from, minute_from, second_from,
		year_to, month_to, day_to, hour_to, minute_to, second_to):
	string_from = "%s-%s-%s %s:%s:%s" % (str(year_from), str(month_from), str(day_from),str(hour_from), str(minute_from), str(second_from))
	string_to = "%s-%s-%s %s:%s:%s" % (str(year_to), str(month_to), str(day_to), str(hour_to), str(minute_to), str(second_to))
	querystring = "SELECT * FROM %s WHERE julianday(logtime) BETWEEN julianday('%s') AND julianday('%s')" % (table, string_from, string_to)
	return query_db(querystring)
	#rows = query_db(querystring)
	#return json.dumps([dict(ix) for ix in rows], default=default)

def _selectDateRange(table, 
		year_from, month_from, day_from, hour_from, minute_from, second_from,
		year_to, month_to, day_to, hour_to, minute_to, second_to):
	string_from = "%s-%s-%s %s:%s:%s" % (str(year_from), str(month_from), str(day_from),str(hour_from), str(minute_from), str(second_from))
	string_to = "%s-%s-%s %s:%s:%s" % (str(year_to), str(month_to), str(day_to), str(hour_to), str(minute_to), str(second_to))
	querystring = "SELECT * FROM %s WHERE julianday(logtime) BETWEEN julianday('%s') AND julianday('%s')" % (table, string_from, string_to)
	rows = query_db(querystring)
	return json.dumps([dict(ix) for ix in rows], default=default)

@app.route('/')
def hello():
    return "Hello World!"

#@app.route('/<name>')
#def hello_name(name):
	#return "Hello {}!".format(name)

@app.route('/query', methods = ['POST'])
def api_query():

	table_exists = ('table' in request.json)
	expression = (('year_from' in request.json) and ('month_from' in request.json) and ('day_from' in request.json) and ('hour_from' in request.json) and ('minute_from' in request.json) and ('second_from' in request.json))
	expression2 = expression and (('year_to' in request.json) and ('month_to' in request.json) and ('day_to' in request.json) and ('hour_to' in request.json) and ('minute_to' in request.json) and ('second_to' in request.json))

	if table_exists and expression and expression2:
		table = request.json['table']
		year_from = request.json['year_from']
		month_from = request.json['month_from']
		day_from = request.json['day_from']
		hour_from = request.json['hour_from']
		minute_from = request.json['minute_from']
		second_from = request.json['second_from']

		year_to = request.json['year_to']
		month_to = request.json['month_to']
		day_to = request.json['day_to']
		hour_to = request.json['hour_to']
		minute_to = request.json['minute_to']
		second_to = request.json['second_to']


		if request.headers['Content-Type'] == 'application/json':
			if request.headers['Accept'] == 'application/json':
				rows = selectDateRange(table, year_from, month_from, day_from, hour_from, minute_from, second_from, year_to, month_to, day_to, hour_to, minute_to, second_to)
				return jsonify({table : json.dumps([dict(ix) for ix in rows], default=default)})
			elif request.headers['Accept'] == 'application/csv':
				rows = selectDateRange(table, year_from, month_from, day_from, hour_from, minute_from, second_from, year_to, month_to, day_to, hour_to, minute_to, second_to)
				_csv = ""
				
				keys = []
				if(len(rows) > 0):
					for column in rows[0].keys():
						keys.append(column)

					for key in keys:
						_csv = _csv + key + ", "
					_csv = _csv + "\n"

					for ix in rows:
						for key in keys:
							_csv = _csv + str(dict(ix)[key]) + ", "
						_csv = _csv + "\n"

				response = make_response(_csv)
				# This is the key: Set the right header for the response
				# to be downloaded, instead of just printed on the browser
				response.headers["Content-Disposition"] = "attachment; filename=sbc_log.csv"
				response.headers["Content-Type"] = "application/csv"
				return response
			else:
				return "415 Unsupported Media Type ;)"
		else:
			return "415 Unsupported Media Type ;)"
	else:
		return "415 Invalid parameters ;)"

	return not_found()

if __name__ == '__main__':
    app.run('10.0.1.7', 8001)

