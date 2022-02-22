#!/usr/bin/python3
#coding: utf-8

# import flask and swagger
from cgi import test
from crypt import methods
from enum import unique
from httplib2 import Response
from markupsafe import escape
from flask import Flask, abort, request, g, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from sqlalchemy_utils import *
from flask_migrate import Migrate
import psycopg2
from localdbconf import bdd_uri as settings
from localdbconf import mdp_admin as mdp_adminnohash
from localdbconf import secret_key, site_key
from flask_bcrypt import Bcrypt
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_recaptcha import ReCaptcha
from flask_babel import Babel, format_datetime, gettext
from datetime import datetime
import locale
import glob
import json
import pytest
              
# creation d'une instance de flask
app = Flask(__name__)


app.config['SECRET_KEY'] = mdp_adminnohash
app.config['RECAPTCHA_USE_SSL']= False
app.config['RECAPTCHA_SITE_KEY']= site_key
app.config['RECAPTCHA_SECRET_KEY']= secret_key
app.config['RECAPTCHA_OPTIONS']= {'theme':'black'}

# Création du captcha     
recaptcha = ReCaptcha(app)

app.config['DEBUG'] = True


# On va chiffrer les donnees de session
app.secret_key = "secret"

# Config multi-lingue
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
babel = Babel(app)

@babel.localeselector
def get_locale():
    return 'en'
    # return request.accept_languages.best_match(['fr', 'en'])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


# On instancie un objet pour le chiffrement
bcrypt = Bcrypt(app)

# On chiffre le mdp admin
mdp_admin = bcrypt.generate_password_hash(mdp_adminnohash).decode('utf-8')

# On garde les donnees de session 2 heures
app.permanent_session_lifetime = timedelta(hours=2)

# On donne la chaine de connexion pour la base de donnees
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(pguser)s:\
%(pgpasswd)s@%(pghost)s:%(pgport)s/%(pgdb)s' % settings

# On instancie un objet de type orm avec la chaine de connection
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# On instancie le modele permettant de formaliser les donnees pour les envoyer a la table Utilisateurs

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifiant = db.Column(db.String(250), unique=True, nullable=False)
    nom = db.Column(db.String(250), unique=True, nullable=True)
    mail = db.Column(db.String(250), unique=False, nullable=False)
    mdp = db.Column(db.String(250), unique=False, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    

    def __init__(self, identifiant, nom, mail, mdp, admin):
        self.identifiant = identifiant
        self.nom = nom
        self.mail = mail
        self.mdp = mdp
        self.admin = admin

class Expediteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(250), unique=True, nullable=False)
    utilisateur_id = db.Column(db.ForeignKey(Utilisateur.id), nullable=False)
    statut = db.Column(db.Integer, unique=False, nullable=False, default=3)
    token = db.Column(db.String(250), unique=True, nullable=True )
    #statut : 1 valide, 2 refuse, 3 en attente

    def __init__(self, mail, utilisateur_id, statut):
        self.mail = mail
        self.utilisateur_id = utilisateur_id
        self.statut = statut
    
class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_mail_postfix = db.Column(db.String(250), unique=True, nullable=False)
    expediteur_id = db.Column(db.ForeignKey(Expediteur.id), nullable=False)
    date = db.Column(db.DateTime)

    def __init__(self, id_mail_postfix, expediteur_id, date):
        self.id_mail_postfix = id_mail_postfix
        self.expediteur_id = expediteur_id
        self.date = date



@app.route('/')      # Possible d'avoir plusieurs routes
@app.route('/index/')
def hello():
    return render_template("index.html")

@app.route('/stats/')
def stats():
    uti = Utilisateur.query.count()
    exp = Expediteur.query.count()
    expvalid = Expediteur.query.filter_by(statut =1).count()
    expblack = Expediteur.query.filter_by(statut =2).count()
    expatt = Expediteur.query.filter_by(statut =3).count()
    mails = Mail.query.count()
    tab = []
    tab.append(uti)
    tab.append(exp)
    tab.append(expvalid)
    tab.append(expblack)
    tab.append(expatt)
    tab.append(mails)

    labels = [gettext("Nombre d'utilisateurs"), gettext("Nombre total d'expéditeurs"), gettext("Nombre d'expéditeurs validés"), gettext("Nombre d'expéditeurs blacklistés"), gettext("Nombre d'expéditeurs en attente"), gettext("Nombre de mails")]

    return render_template("stats.html", tab= json.dumps(tab), labels= json.dumps(labels))
    # return render_template("stats.html", uti= json.dumps(uti), exp=json.dumps(exp), expvalid=json.dumps(expvalid), expblack=json.dumps(expblack), expatt=json.dumpsexpatt, mails=mails)

@app.route('/statut/')
def statut():
    db = True
    postfix = True 
    app = True
    c1=0
    c2=0
    c3=0
    # db.session.
    test = Utilisateur
    if not test:
        db = False
    if (db):
        mess1= "Base de données fonctionnelle \n"
        c1=1
    else:
        mess1= "Base de données non-fonctionnelle \n"
    if (postfix):
        mess2 = "Serveur postfix fonctionnel \n"
        c2=1
    else:
        mess2 = "Serveur postfix non-fonctionnel \n"
    if(app):
        mess3 = "Application fonctionnelle"
        c3=1
    else:
        mess3 = "Application non-fonctionnelle"
        # abort(400)
    # flash(mess)
    # return redirect(url_for('hello'))
    if c1+c2+c3 == 3:
        # abort(200, mess)
        return render_template("index.html", c1=c1, c2=c2, c3=c3 ), 200
        # return redirect(url_for("hello", mess=mess)), 200
    else:
        return render_template("index.html", c1=c1, c2=c2, c3=c3 ), 500
        # abort(500, mess)
 
@app.route('/validation/', methods=["GET", "POST"])
def validation():
    message = '' 
    if request.method == 'POST': 
        if recaptcha.verify(): # On vérifie si le captcha a été validé 
            message = gettext('Captcha validé') # Send success message
            # expediteur = Expediteur.query.filter_by(mail=token).first()
            # expediteur.statut = 1
            # db.session.commit()  
            # expmail = request.form.get('email')
            # token = request.form.get('email')
            # expediteur = Expediteur.query.filter_by(mail=token).first()
            # if expediteur:
            #     if expediteur.token == token:
            #         message= gettext('Adresse ') + expmail + gettext(' bien validée') 
            #         expediteur.statut=1
            #         # mails = Mail.query.filter_by(expediteur_id=expediteur.id)
            #         # for mail in mails:
            #             # db.session.delete(mail)
            #         db.session.commit()
            #     else:
            #         message= gettext('Token invalide')
            # else:
            #     message= gettext('Adresse de messagerie invalide')
        else:
            message = gettext('Veuillez valider le captcha') # Send error message
    return render_template('validation.html', message=message)

# Redirection
@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    utilisateurs = Utilisateur.query
    if request.method == 'POST': 
        mail = request.form['mail']
        action = request.form['act']
        utilisateur = Utilisateur.query.filter_by(mail=mail).first()
        session['identifiant'] = utilisateur.identifiant
        if action == "Expediteur":
            return redirect(url_for("consultexp"))   
        else:
            if action == "Mails en attente" or action == "Pending mails":
                return redirect(url_for("consultmails"))
            else:
                return redirect(url_for("consultmailsblacklist"))
    else:
        flash(gettext("Bienvenue") +f", {session['nom']}")
        return render_template("admin.html", utilisateurs=utilisateurs)

@app.route('/user/', methods=["GET", "POST"])
def user():
    # email = None # On definit l'email
    try:
        if 'mail' in session:
            found_user = Utilisateur.query.filter_by(mail=session['mail']).first() # On verifie si il existe un utilisateur avec cet email dans la bdd
            if found_user.admin:
                return redirect(url_for("admin"))
            else:
            # if request.method == "POST":    # On definit l'email
            #     email = request.form['email']
            #     session['email'] = email
            #     found_user =Utilisateurs.query.filter_by(email=user).first()
            #     found_user.email = email
            #     db.session.commit()
            #     flash("Email bien pris en compte", "connecte") #Utiliser 2 eme arg pour mettre une icone

            # else:
            #     if "email" in session:
            #         mail = session["email"]

            # return render_template("user.html", mail=mail)
        # else:
                flash(gettext("Bienvenue")+f", {session['identifiant']}")
                return render_template("user.html")
        else:
            flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))

    except IndexError:
        abort(404)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "POST":
            session.permanent = True
            identifiant = request.form['identifiant'] # On donne en parametre dans la requete POST 
            mdp = request.form['mdp']
            found_user = Utilisateur.query.filter_by(identifiant=identifiant).first() # On verifie si il existe un utilisateur avec cet email dans la bdd
            if found_user:
                if bcrypt.check_password_hash(found_user.mdp, mdp): # returne vrai si les mots de passe sont les memes sans chiffrement
                    session['identifiant'] = found_user.identifiant
                    session['nom'] = found_user.nom
                    session['mail'] = found_user.mail
                    session['mdp'] = found_user.mdp
                    session['admin'] = found_user.admin
                    if found_user.admin:
                        return redirect(url_for("admin"))
                    else:
                        return redirect(url_for('user'))
                else:
                    return render_template("loginwrong.html")
            else:
                return render_template("loginwrong.html")
        else:
            if 'identifiant' in session:
                flash(gettext("Compte déjà connecté"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("login.html")
    except IndexError:
        abort(404)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == "POST":
            session.permanent = True
            nom = request.form['nm'] # On donne en parametre dans la requete POST 
            identifiant = request.form['identifiant']            
            mdp = bcrypt.generate_password_hash(request.form['mdp']).decode('utf-8') # On chiffre le mot de passe
            mail = request.form['mail']
            mdpadmin = request.form['mdpad']
            found_user = Utilisateur.query.filter_by(identifiant=identifiant).first()
            if found_user:
                flash(gettext("Utilisateur déja inscrit"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                return render_template("signup.html")
            else:
                if  bcrypt.check_password_hash(mdp_admin, mdpadmin):
                    admin=True
                else:
                    admin=False
                session['identifiant'] = identifiant
                session['nom'] = nom
                session['mail'] = mail # On definit les variables de session
                session['mdp'] = mdp
                session['admin'] = admin
                usr = Utilisateur(identifiant, nom, mail, mdp, admin)
                db.session.add(usr)
                db.session.commit() # On envoie usr qui sera une ligne dans la bdd
                flash(gettext("Inscription reussie"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
        else:
            if 'identifiant' in session:
                flash(gettext("Compte déjà connecté"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                return redirect(url_for("user"))
            else:
                return render_template("signup.html")

    except IndexError:
        abort(404)

@app.route('/logout/')
def logout():
    if 'identifiant' in session:
        flash(f"{session['identifiant']} deconnecte avec succes", "deconnecte") #Utiliser 2 eme arg pour mettre une icone
    else: 
        flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
    session.pop('identifiant', None) # On supprime les variables de session
    session.pop('nom', None) # On supprime les variables de session
    session.pop('mail', None)  
    session.pop('mdp', None)  
    session.pop('admin', None)
    return redirect(url_for("login"))

@app.route('/consultmails/', methods=['GET', 'POST'])
def consultmails():
    try:
        if 'identifiant' in session:
            users = Utilisateur.query.filter_by(identifiant=session['identifiant']).first()
            expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id, statut =3).all()
            t= []
            for e in expediteurs:
                t.append(e.id)
            # print(t,file=sys.stderr)

            lmails= Mail.query.filter(Mail.expediteur_id.in_(t))
            # print(lmails,file=sys.stderr)
            # lmails= Mail.query.filter_by(expediteur_id=expediteurs.id)
            if request.method == "POST":
                expediteur = request.form.get('sender')
                return redirect(url_for("consultmailsexp", expediteur=expediteur))
                # if request.json:
                #     tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
                #     print(tab,file=sys.stderr)
                # else:
                #     mail = request.form.get('mail')
                #     expediteur = Expediteur.query.filter_by(mail=mail).first()
                #     lmails= Mail.query.filter_by(expediteur_id=expediteur.id)
                # if request.json:
                #     tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
                #     print(tab,file=sys.stderr)
                # for exps in tab: 
                #     exp = Expediteur.query.filter_by(mail=exps['mail']).first()
                #     if exps['statut']=='1':
                #         exp.statut = 1
                #     else:
                #         if exps['statut']=='2':
                #             exp.statut = 2
                #         else:
                #             exp.statut = 3
                # db.session.commit()
                    # flash("Veuillez recharger la page")
                # return render_template("consultmails.html", identifiant=session['identifiant'], expediteurs=expediteurs, lmails=lmails)
            else:
                if 'nom' in session:
                    return render_template("consultmails.html", identifiant=session['identifiant'], expediteurs=expediteurs, lmails=lmails)
                else:
                    flash(gettext("Modifications bien prises en compte"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                    return render_template("login.html")
        else:
            flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))
    except IndexError:
        abort(404)

@app.route('/consultmailsexp/<expediteur>', methods=['GET', 'POST'])
def consultmailsexp(expediteur):
    try:
        if 'identifiant' in session:
            users = Utilisateur.query.filter_by(identifiant=session['identifiant']).first()
            exp = Expediteur.query.filter_by(utilisateur_id=users.id, mail= expediteur).first()
            lmails= Mail.query.filter_by(expediteur_id = exp.id).all()
            print(lmails, file=sys.stderr)
            if request.method == "POST":
                if request.json:
                    tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
                    print(tab,file=sys.stderr)
                return render_template("consultmailsexp.html", identifiant=session['identifiant'], expediteur=expediteur, lmails=lmails)
            else:
                if 'nom' in session:
                    return render_template("consultmailsexp.html", identifiant=session['identifiant'], expediteur=expediteur, lmails=lmails)
                else:
                    flash(gettext("Modifications bien prises en compte"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                    return render_template("login.html")
        else:
            flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))
    except IndexError:
        abort(404)

@app.route('/consultmailsblacklist/', methods=['GET', 'POST'])
def consultmailsblacklist():
    try:
        if 'identifiant' in session:
            users = Utilisateur.query.filter_by(identifiant=session['identifiant']).first()
            expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id, statut =2).all()
            t= []
            for e in expediteurs:
                t.append(e.id)
            lmails= Mail.query.filter(Mail.expediteur_id.in_(t))

            if request.method == "POST":
                expediteur = request.form.get('sender')
                return redirect(url_for("consultmailsexp", expediteur=expediteur))
                # if request.json:
                #     tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
                #     print(tab,file=sys.stderr)
                # else:
                #     mail = request.form.get('mail')
                #     expediteur = Expediteur.query.filter_by(mail=mail).first()
                #     lmails= Mail.query.filter_by(expediteur_id=expediteur.id)
                # return render_template("consultmails.html", identifiant=session['identifiant'], expediteurs=expediteurs, lmails=lmails)
            else:
                if 'nom' in session:
                    return render_template("consultmails.html", identifiant=session['identifiant'], expediteurs=expediteurs, lmails=lmails)
                else:
                    flash(gettext("Modifications bien prises en compte"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                    return render_template("login.html")
        else:
            flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))
    except IndexError:
        abort(404)

@app.route('/api/modifmails/', methods=['GET', 'POST'])
def modifmails():
    try:
        if request.method == "POST":
            tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
            print(tab,file=sys.stderr)
            for mails in tab: 
                mail = Mail.query.filter_by(id=mails['identifiant']).first()
                if mails['statut']=='supprimé':
                    db.session.delete(mail)
            db.session.commit()
            return render_template("consultmails.html", )
    except IndexError:
        abort(404)
        
@app.route('/consultexp/', methods=['GET', 'POST'])
def consultexp():
    try:
        if 'identifiant' in session:
            users = Utilisateur.query.filter_by(identifiant=session['identifiant']).first()
            expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id)
            t = dict()
            for exp in expediteurs:
                mails = Mail.query.filter_by(expediteur_id=exp.id).count()
                t[exp.mail] = mails
            print(t, file=sys.stderr)
            # mails = Mail.query.filter_by(expediteur_id = expediteurs.id)
            if request.method == "POST":
                tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
                for exps in tab: 
                    exp = Expediteur.query.filter_by(mail=exps['mail']).first()
                    if exps['statut']=='1':
                        exp.statut = 1
                    else:
                        if exps['statut']=='2':
                            exp.statut = 2
                            # on va supprimer ses mails d
                        else:
                            exp.statut = 3
                db.session.commit()
                flash(gettext("Modifications bien prises en compte"))
                return render_template("consultexp.html", identifiant=session['identifiant'], users=users, expediteurs=expediteurs, t=t)
            else:
                if 'nom' in session:
                    return render_template("consultexp.html", identifiant=session['identifiant'], users=users, expediteurs=expediteurs, t=t)
                else:
                    flash(gettext("Pas de compte connecté"), "connecte") #Utiliser 2 eme arg pour mettre une icone
                    return render_template("login.html")
        else:
            flash(gettext("Pas de compte connecté"), "deconnecte") #Utiliser 2 eme arg pour mettre une icone
            return redirect(url_for("login"))
    except IndexError:
        abort(404)

@app.route('/status/', methods=['GET', 'POST'])
def status():
    try:
        if request.method == "POST":
            tab = request.get_json(force=true)['paramName'] # On recupere la liste au format json des emails
            print(tab,file=sys.stderr)
            for mails in tab: 
                mail = Mail.query.filter_by(id=mails['identifiant']).first()
                if mails['statut']=='supprimé':
                    db.session.delete(mail)
            db.session.commit()
            return render_template("consultmails.html", )
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
    db.init_app(app)
    db.create_all()
