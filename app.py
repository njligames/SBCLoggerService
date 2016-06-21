from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
	return "Hello {}!".format(name)

#http://10.0.1.17:5000
if __name__ == '__main__':
    app.run('10.0.1.17', 8080)
