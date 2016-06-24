from flask import Flask
from flask import Response
from flask import json

app = Flask(__name__)


#@app.route('/')
#def hello():
    #return "Hello World!"

#@app.route('/<name>')
#def hello_name(name):
	#return "Hello {}!".format(name)

@app.route('/hello', methods = ['GET'])
def api_hello():
	data = {'hello'  : 'world','number' : 3}
	js = json.dumps(data)

	resp = Response(js, status=200, mimetype='application/json')
	resp.headers['Link'] = 'http://luisrei.com'

	return resp

#http://10.0.1.17:5000
if __name__ == '__main__':
    app.run('10.0.1.17', 8080)
