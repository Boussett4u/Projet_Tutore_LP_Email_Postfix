# import flask and swagger
from cgi import test
from crypt import methods
from markupsafe import escape
from flask import Flask, abort, request, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy_utils import *
from flask_migrate import Migrate
import psycopg2
from localdbconf import bdd_uri as settings
from flask_bcrypt import Bcrypt
              
# creation d'une instance de flask
app = Flask(__name__)

app.config['DEBUG'] = True

# On va chiffrer les données de session
app.secret_key = "secret"

# On instancie un objet pour le chiffrement
bcrypt = Bcrypt(app)

# On garde les données de session 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

# On donne la chaîne de connexion pour la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(pguser)s:\
%(pgpasswd)s@%(pghost)s:%(pgport)s/%(pgdb)s' % settings

# On instancie un objet de type orm avec la chaine de connection
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# On instancie le modèle permettant de formaliser les données pour les envpyer à la table Utilisateurs
class Utilisateurs(db.Model):
    __tablename__ = 'Utilisateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String())
    email = db.Column(db.String())
    mdp = db.Column(db.String())
    admin = db.Column(db.Boolean)

# Cela permet d'envoyer les données vers la bdd

    def __init__(self, nom, email, mdp):
        self.nom = nom
        self.email = email
        self.mdp = mdp


@app.route('/')      # Possible d'avoir plusieurs routes
@app.route('/index/')
def hello():
    return render_template("index.html")

# Redirection
@app.route('/admin/')
def admin():
    return render_template("admin.html")
    # return redirect(url_for("capitalize", word="lol"))

@app.route('/user', methods=["GET", "POST"])
def user():
    email = None # On définit l'email
    try:
        if 'nom' in session:
            # if request.method == "POST":    # On définit l'email
            #     email = request.form['email']
            #     session['email'] = email
            #     found_user =Utilisateurs.query.filter_by(email=user).first()
            #     found_user.email = email
            #     db.session.commit()
            #     flash("Email bien pris en compte", "connecté") #Utiliser 2 eme arg pour mettre une icone

            # else:
            #     if "email" in session:
            #         mail = session["email"]

            # return render_template("user.html", mail=mail)
        # else:
            flash(f"Bienvenue, {session['nom']}")
            return render_template("user.html")
        else:
            flash("Pas de compte connecté", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))

    except IndexError:
        abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "POST":
            # session.permanent = True
            email = request.form['email'] # On donne en parametre dans la requete POST 
            mdp = request.form['mdp']
            found_user = Utilisateurs.query.filter_by(email=email).first() # On vérifie si il existe un utilisateur avec cet email dans la bdd
            if found_user:
                if bcrypt.check_password_hash(found_user.mdp, mdp): # returne vrai si les mots de passe sont les mêmes sans chiffrement
                    session['nom'] = found_user.nom
                    session['email'] = found_user.email
                    session['mdp'] = found_user.mdp
                    flash("Bien connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                    return redirect(url_for("user"))
                else:
                    return render_template("loginwrong.html")
            else:
                return render_template("loginwrong.html")
        else:
            if 'nom' in session:
                flash("Déja connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("login.html")
    except IndexError:
        abort(404)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == "POST":
            # session.permanent = True
            nom = request.form['nm'] # On donne en parametre dans la requete POST 
            email = request.form['email']            
            mdp = bcrypt.generate_password_hash(request.form['mdp']).decode('utf-8') # On chiffre le mot de passe
            found_user = Utilisateurs.query.filter_by(email=email).first()
            if found_user:
                flash(f"Utilisateur {session['nom']} déja insrit", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return render_template("signup.html")
            else:
                session['nom'] = nom
                session['email'] = email # On définit les variables de session
                session['mdp'] = mdp
                usr = Utilisateurs(nom, email, mdp)
                db.session.add(usr) 
                db.session.commit() # On envoie usr qui sera une ligne dans la bdd
                flash("Inscription réussie", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
        else:
            if 'user' in session:
                flash(f"Utilisateur {session['nom']} connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("signup.html")

    except IndexError:
        abort(404)

@app.route('/logout')
def logout():
    if 'nom' in session:
        flash(f"{session['nom']} déconnecté avec succès", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
    else: 
        flash("Pas de compte connecté", "deconnecté") #Utiliser 2 eme arg pour mettre une icone
    session.pop('nom', None) # On supprime les variables de session
    session.pop('email', None)  
    session.pop('mdp', None)  
    return redirect(url_for("login"))


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
    db.init_app(app)
