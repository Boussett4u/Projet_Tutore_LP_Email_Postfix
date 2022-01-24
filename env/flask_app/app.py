# import flask and swagger
from crypt import methods
from markupsafe import escape
from flask import Flask, abort, request, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from sqlalchemy import create_engine  
from sqlalchemy import Column, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker

# creation d'une instance de flask
app = Flask(__name__)

# On va chiffrer les données de session
app.secret_key = "secret"

# Cette chaîne nous permet de nous connecter à la bdd
bdd_uri = "postgresql://postgres:nael2001@localhost:5432/test"

# On garde les données de session 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

# On crée une instance de moteur de bdd
# db = create_engine(bdd_uri)  

# On crée une session pour pouboir utiliser l'orm et ne pas travailler avec du SQL
# Session = sessionmaker(bind=db)

# Ajouter dans une table exemple
# book = Book( c'est un objet appartenant a la table book
#     title='Deep Learning',
#     author='Ian Goodfellow',
#     pages=775,
#     published=datetime(2016, 11, 18)
# )
# s = Session()
# s.add(book)
# s.commit()
# s.query(Book).first On peut vérifier si ça a été envoyé sur la base
# s.close_all()
# recreate_database()

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
            # session.permanent = True
            user = request.form['nm'] # On donne en parametre dans la requete POST 
            mdp = request.form['mdp']
            # trouve=0
            # s = Session()
            # utilisateurs = session.query(Utilisateurs)
            # for utilisateur in utilisateurs:
            #     if mdp == utilisateur.mdp and user == utilisateur.email:
            #         trouve=1
            # # if mdp == "lol" and user == "lol":
            #         session['user'] = user # On définit les variables de session
            #         session['mdp'] = mdp
            # if trouve==1:
            #     flash("Bien connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
            #     return redirect(url_for("user"))
            # else:
            #     return render_template("loginwrong.html")
        else:
            if 'user' in session:
                flash("Déja connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("login.html")
            # s.close_all()
    except IndexError:
        abort(404)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == "POST":
            # session.permanent = True
            user = request.form['nm'] # On donne en parametre dans la requete POST 
            mdp = request.form['mdp']
            email =request.form['email']
            # s = Session()
            # utilisateurs = session.query(Utilisateurs)
            # for utilisateur in utilisateurs:
            #     if user != utilisateur.email:
            # # if mdp == "lol" and user == "lol":
            #         session['user'] = user # On définit les variables de session
            #         session['mdp'] = mdp
            #         user = Utilisateurs( 
            #             email='{email}',
            #             mdp='{mdp}',
            #         )
            #         s = Session()
            #         s.add(user)
            #         s.commit()
            #         flash("Inscription réussie", "connecté") #Utiliser 2 eme arg pour mettre une icone
            #         return redirect(url_for("user"))
            # else:
            #     flash(f"Utilisateur {session['user']} déja insrit", "connecté") #Utiliser 2 eme arg pour mettre une icone
            #     return render_template("signup.html")
        else:
            if 'user' in session:
                flash(f"Utilisateur {session['user']} connecté", "connecté") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("signup.html")
            # s.close_all()
            # recreate_database()
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
                mail = request.form['mail']
                session['mail'] = mail
                flash("Email bien pris en compte", "connecté") #Utiliser 2 eme arg pour mettre une icone

            else:
                if "mail" in session:
                    mail = session["email"]

            return render_template("user.html", mail=mail)
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

