# import flask and swagger
from markupsafe import escape
from flask import Flask, abort, request, redirect, url_for, render_template

# creation d'une instance de flask
app = Flask(__name__)


@app.route('/')      # Possible d'avoir plusieurs routes
@app.route('/index/')

def hello():
    return '<h1>Hello, World!</h1>'

# Redirection
@app.route('/admin/')
def admin():
    return redirect(url_for("capitalize", word="lol"))

@app.route('/about/<nael>') # Utilisation de pages HTML
def about(nael):
    return render_template("index.html",holla=nael, r=2, noms=["lol", "lul", "lil"]) 

@app.route('/capitalize/<word>/') # On a accès <word> avec la variable word
def capitalize(word):
    return '<h1>Hello {} !</h1>'.format(escape(word.capitalize())) # .format ajoute ce qu'on lui donne à la place de {} 
# .escape convertit les caracteres non alphanumeriques en String
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

@app.route('/entities/', methods=['GET', 'POST'])
def entities():
    if request.method == "GET":
        return {
            'message': 'This endpoint should return a list of entities',
            'method': request.method
        }
    if request.method == "POST":
        return {
            'message': 'This endpoint should create an entity',
            'method': request.method,
		'body': request.json
        }

@app.route('/entities/<int:entity_id>/', methods=['GET', 'PUT', 'DELETE'])
def entity(entity_id):
    if request.method == "GET":
        return {
            'id': entity_id,
            'message': 'This endpoint should return the entity {} details'.format(entity_id),
            'method': request.method
        }
    if request.method == "PUT":
        return {
            'id': entity_id,
            'message': 'This endpoint should update the entity {}'.format(entity_id),
            'method': request.method,
		'body': request.json
        }
    if request.method == "DELETE":
        return {
            'id': entity_id,
            'message': 'This endpoint should delete the entity {}'.format(entity_id),
            'method': request.method
        }

# permet de lancer l'appli
# if __name__ == "__main__":
#     app.run()
