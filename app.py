from flask import Flask
from flask import Response
from flask import json
import sqlite3
from flask import g
import json

app = Flask(__name__)

DATABASE = "/usr/data/test.db"

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
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

def selectSpatialDataChange_Range(start, end):
	ret = []
	querystring = "select * from SPATIAL_DATACHANGE where julianday(logtime) between julianday('2011-01-01') and julianday('now')"
	for datapoint in query_db(querystring):
		d = {}
		d['primary_key'] = datapoint[0]
		d['logtime'] = datapoint[1]
		d['serialnumber'] = datapoint[2]
		d['idx'] = datapoint[3]
		d['acceleration_x'] = datapoint[4]
		d['acceleration_y'] = datapoint[5]
		d['acceleration_z'] = datapoint[6]
		d['angularrate_x'] = datapoint[7]
		d['angularrate_y'] = datapoint[8]
		d['angularrate_z'] = datapoint[9]
		d['magneticfield_x'] = datapoint[10]
		d['magneticfield_y'] = datapoint[11]
		d['magneticfield_z'] = datapoint[12]
		ret.append(json.dumps(d))
	return ret

@app.route('/')
def hello():
    return "Hello World!"

#@app.route('/<name>')
#def hello_name(name):
	#return "Hello {}!".format(name)

@app.route('/spatial', methods = ['GET'])
def api_hello():
	mydata = selectSpatialDataChange_Range(0,0)
	js = json.dumps(mydata)

	resp = Response(js, status=200, mimetype='application/json')
	resp.headers['Link'] = 'http://luisrei.com'

	return resp

#http://10.0.1.17:5000
if __name__ == '__main__':
    app.run('10.0.1.17', 8001)
