from markupsafe import escape
from flask import Flask, abort
# from flask_restplus import Api, Resource
# app = Api(app = flask_app)

# name_space = app.namespace('main', description='Main APIs')

app = Flask(__name__)

# @name_space.route("/")
# class MainClass(Resource):
# 	def get(self):
# 		return {
# 			"status": "Got new data"
# 		}
# 	def post(self):
# 		return {
# 			"status": "Posted new data"
# 		}
@app.route('/')
@app.route('/index/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/about/')
def about():
    return '<h3>This is a Flask web application.</h3>'

@app.route('/capitalize/<word>/')
def capitalize(word):
    return '<h1>{}</h1>'.format(escape(word.capitalize()))

@app.route('/add/<int:n1>/<int:n2>/')
def add(n1, n2):
    return '<h1>{}</h1>'.format(n1 + n2)

@app.route('/users/<int:user_id>/')
def greet_user(user_id):
    users = ['Bob', 'Jane', 'Adam']
    try:
        return '<h2>Hi {}</h2>'.format(users[user_id])
    except IndexError:
        abort(404)