# import flask and swagger
from crypt import methods
from markupsafe import escape
from flask import Flask, abort, request, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLalchemy

# creation d'une instance de flask
app = Flask(__name__)

# On va chiffrer les données de session
app.secret_key = "secret"

# On configure la table users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# On garde les données de session 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

# On crée une instance de bdd
db = SQLalchemy(app)


@app.route('/')      # Possible d'avoir plusieurs routes
@app.route('/index/')
def hello():
    return render_template("index.html")

# Redirection
@app.route('/admin/')
def admin():
    return render_template("admin.html")
    # return redirect(url_for("capitalize", word="lol"))

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "POST":
            session.permanent = True
            user = request.form['nm'] # On donne en parametre dans la requete POST 
            mdp = request.form['mdp']
            session['user'] = user # On définit les variables de session
            session['mdp'] = mdp
            if mdp == "lol" and user == "lol":
                flash("Bien connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("loginwrong.html")
        else:
            if 'user' in session:
                flash("Déja connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("login.html")
    except IndexError:
        abort(404)

@app.route('/logout')
def logout():
    if 'user' in session:
            flash(f"{session['user']} déconnecté avec succès", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
    else: 
            flash("Pas de compte connecté", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
    session.pop('user', None)
    session.pop('mdp', None)  
    session.pop('email', None)  
    return redirect(url_for("login"))

@app.route('/user', methods=["GET", "POST"])
def user():
    email = None # On définit l'email
    try:
        if 'user' in session:
            if request.method == "POST":    # On définit l'email
                email = request.form['email']
                session['email'] = email
                flash("Email bien pris en compte", "connecté") #Utiliser 2 eme arg pour mettre une icone

            else:
                if "email" in session:
                    email = session["email"]

            return render_template("user.html", email=email)
        else:
            flash("Pas de compte connecté", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))
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
if __name__ == "__main__":
    app.run(debug=True)

