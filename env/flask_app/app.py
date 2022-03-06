#!/usr/bin/python3
#coding: utf-8

# import flask and swagger
from cgi import test
from crypt import methods
from enum import unique
from re import S
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
from config import bdd_uri as settings
from config import *

from flask_bcrypt import Bcrypt
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_recaptcha import ReCaptcha
from flask_babel import Babel, format_datetime, gettext
from datetime import datetime
from datetime import date
import locale
import glob
import json
import pytest
from db import *
# from db import models

# config captcha
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

db.init_app(app)


# Possible d'avoir plusieurs routes
@app.route('/')      
@app.route('/index/')
def hello():
    return render_template("index.html")

@app.route('/stats/')
def stats():
    uti = Utilisateur.query.count()
    exp = Expediteur.query.count()
    expvalid = Expediteur.query.filter_by(statut = ACCEPTED).count()
    expblack = Expediteur.query.filter_by(statut = REFUSED).count()
    expatt = Expediteur.query.filter_by(statut = UNDECIDED).count()
    mails = Mail.query.count()
    tab = []
    tab.append(uti)
    tab.append(exp)
    tab.append(expvalid)
    tab.append(expblack)
    tab.append(expatt)
    tab.append(mails)
    
    labels = [gettext("Nombre d'utilisateurs"), gettext("Nombre total d'expéditeurs"), gettext("Nombre d'expéditeurs validés"), gettext("Nombre d'expéditeurs blacklistés"), gettext("Nombre d'expéditeurs en attente"), gettext("Nombre de mails")]

    acceptedmails = Statistiques.query.filter_by(actionFiltre= ACCEPTED).all()
    refusedmails = Statistiques.query.filter_by(actionFiltre= REFUSED).all()
    undefinedmails = Statistiques.query.filter_by(actionFiltre= UNDECIDED).all()

    nbacceptedmails= Statistiques.query.filter_by(actionFiltre= ACCEPTED).count() 
    nbrefusedmails= Statistiques.query.filter_by(actionFiltre= REFUSED).count()
    nbundefinedmails= Statistiques.query.filter_by(actionFiltre= UNDECIDED).count()

    listacceptedmails =[0,0,0,0,0,0,0,0,0,0,0,0]
    listrefusedmails =[0,0,0,0,0,0,0,0,0,0,0,0] 
    listundefinedmails =[0,0,0,0,0,0,0,0,0,0,0,0]

    
    index=0


    for mail in acceptedmails:
        index = int(mail.date.strftime("%m"))-1
        listacceptedmails[index]+=1

    for mail in refusedmails: 
        index = int(mail.date.strftime("%m"))-1
        listrefusedmails[index]+=1

    for mail in undefinedmails: 
        index = int(mail.date.strftime("%m"))-1
        listundefinedmails[index]+=1

    for i in range(11):
        listacceptedmails[i+1]+=listacceptedmails[i] 
        listrefusedmails[i+1]+=listrefusedmails[i] 
        listundefinedmails[i+1]+=listundefinedmails[i] 

    return render_template("stats.html", tab= json.dumps(tab), labels= json.dumps(labels), nbacceptedmails=nbacceptedmails, nbrefusedmails=nbrefusedmails, nbundefinedmails=nbundefinedmails, listacceptedmails= json.dumps(listacceptedmails), listrefusedmails= json.dumps(listrefusedmails), listundefinedmails= json.dumps(listundefinedmails),mails=mails, exp=exp, uti=uti)

@app.route('/statut/')
def statut():
    postfix = True 
    app = True
    c1=0
    c2=0
    c3=0
    db = Utilisateur
    if (db):
        c1=1
    if (postfix):
        c2=1
    if(app):
        c3=1
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
 
@app.route('/validation/<token>', methods=["GET", "POST"])
def validation(token):
    message = '' 
    expediteur = Expediteur.query.filter_by(token=token).first()
    if expediteur.statut != ACCEPTED:
        if request.method == 'POST': 
            # On vérifie si le captcha a été validé 
            if recaptcha.verify(): 
                message = gettext('Captcha validé') 
                expediteur.statut = ACCEPTED
                db.session.commit()
        else:
            message = gettext('Veuillez valider le captcha') 
    else:
        message = gettext('Expediteur ' + expediteur.mail + ' deja valide') 
    return render_template('validation.html', message=message, mail = expediteur.mail)

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

# Redirection
@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    utilisateurs = Utilisateur.query
    if request.method == 'POST': 
        mail = request.form['mail']
        action = request.form['act']
        utilisateur = Utilisateur.query.filter_by(mail=mail).first()
        session['mail'] = utilisateur.mail
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
        if 'mail' not in session:
            #Utiliser 2 eme arg pour mettre une icone
            flash(gettext("Pas de compte connecté"), "deconnecte") 
            return redirect(url_for("login"))
        # On verifie si il existe un utilisateur avec cet email dans la bdd
        found_user = Utilisateur.query.filter_by(mail=session['mail']).first() 
        if found_user.admin:
            return redirect(url_for("admin"))
        flash(gettext("Bienvenue")+f", {session['nom']}")
        return render_template("user.html")
    except IndexError:
        abort(404)
	


@app.route('/login/', methods=['GET', 'POST'])
def login():    
    try:
        if 'mail' in session:
            #Utiliser 2 eme arg pour mettre une icone
            flash(gettext("Compte déjà connecté"), "connecte") 
            return redirect(url_for("user"))
        if request.method == "POST":
            session.permanent = True
            # On donne en parametre dans la requete POST 
            mail = request.form['mail'] 
            mdp = request.form['mdp']
            # On verifie si il existe un utilisateur avec cet email dans la bdd
            found_user = Utilisateur.query.filter_by(mail=mail).first() 
            if found_user:
                 # returne vrai si les mots de passe sont les memes sans chiffrement
                if bcrypt.check_password_hash(found_user.mdp, mdp):
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
        return render_template("login.html")
    except IndexError:
        abort(404)



@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    try:
        if 'mail' in session:
            flash(gettext("Compte déjà connecté"), "connecte") 
            return redirect(url_for("user"))
        if request.method == "POST":
            session.permanent = True
            # On donne en parametre dans la requete POST   
            nom = request.form['nm']        
            # On chiffre le mot de passe
            mdp = bcrypt.generate_password_hash(request.form['mdp']).decode('utf-8') 
            mail = request.form['mail']
            mdpadmin = request.form['mdpad']
            found_user = Utilisateur.query.filter_by(mail=mail).first()
            if found_user:
                flash(gettext("Utilisateur déja inscrit"), "connecte") 
                return render_template("signup.html")
            if  bcrypt.check_password_hash(mdp_admin, mdpadmin):
                admin=True
            else:
                admin=False
            # On definit les variables de session
            session['nom'] = nom
            session['mail'] = mail 
            session['mdp'] = mdp
            session['admin'] = admin
            usr = Utilisateur(nom, mail, mdp, admin)
            db.session.add(usr)
            db.session.commit() 
            flash(gettext("Inscription reussie"), "connecte") 
            return redirect(url_for("user"))        
        return render_template("signup.html")
    except IndexError:
        abort(404)
	

@app.route('/logout/')
def logout():
    if 'email' in session:
        flash(f"{session['nom']} deconnecte avec succes", "deconnecte") 
    else: 
        flash(gettext("Pas de compte connecté"), "deconnecte") 
    # On supprime les variables de session
    session.pop('nom', None) 
    session.pop('mail', None)  
    session.pop('mdp', None)  
    session.pop('admin', None)
    return redirect(url_for("login"))

@app.route('/consultmails/', methods=['GET', 'POST'])
def consultmails():
    try:
        if 'mail' not in session:
            flash(gettext("Pas de compte connecté"), "deconnecte")
            return redirect(url_for("login"))
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id, statut =UNDECIDED).all()
        t= []
        for e in expediteurs:
            t.append(e.id)
        lmails= Mail.query.filter(Mail.expediteur_id.in_(t))
        if request.method == "POST":
            expediteur = request.form.get('sender')
            return redirect(url_for("consultmailsexp", expediteur=expediteur))

        return render_template("consultmails.html", mail=session['mail'], expediteurs=expediteurs, lmails=lmails)
    except IndexError:
        abort(404)

@app.route('/consultallmails/', methods=['GET', 'POST'])
def consultallmails():
    try:
        if 'mail' not in session:
            flash(gettext("Pas de compte connecté"), "deconnecte")
            return redirect(url_for("login"))
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id).all()
        t= []
        for e in expediteurs:
            t.append(e.id)
        lmails= Mail.query.filter(Mail.expediteur_id.in_(t))
        if request.method == "POST":
            expediteur = request.form.get('sender')
            return redirect(url_for("consultmailsexp", expediteur=expediteur))

        return render_template("consultmails.html", mail=session['mail'], expediteurs=expediteurs, lmails=lmails)
    except IndexError:
        abort(404)	

@app.route('/consultmailsexp/<expediteur>', methods=['GET', 'POST'])
def consultmailsexp(expediteur):
    try:
        if 'mail' not in session:
            flash(gettext("Pas de compte connecté"), "deconnecte") 
            return redirect(url_for("login"))
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        exp = Expediteur.query.filter_by(utilisateur_id=users.id, mail= expediteur).first()
        lmails= Mail.query.filter_by(expediteur_id = exp.id).all() 
        if request.method == "POST":
           if request.json:
               # On recupere la liste au format json des emails
               tab = request.get_json(force=true)['paramName'] 
        return render_template("consultmailsexp.html", mail=session['mail'], expediteur=expediteur, lmails=lmails)
    except IndexError:
        abort(404)
	

@app.route('/consultmailsblacklist/', methods=['GET', 'POST'])
def consultmailsblacklist():
    try:
        if 'mail' not in session:
            flash(gettext("Pas de compte connecté"), "deconnecte") 
            return redirect(url_for("login"))
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id, statut =REFUSED).all()
        t= []
        for e in expediteurs:
            t.append(e.id)
        lmails= Mail.query.filter(Mail.expediteur_id.in_(t))
        if request.method == "POST":
            expediteur = request.form.get('sender')
            return redirect(url_for("consultmailsexp", expediteur=expediteur))
        return render_template("consultmails.html", mail=session['mail'], expediteurs=expediteurs, lmails=lmails)
    except IndexError:
        abort(404)
	
@app.route('/api/modifmails/', methods=['GET', 'POST'])
def modifmails():
    try:
        if request.method == "POST":
            tab = request.get_json(force=true)['paramName'] 
            for mails in tab: 
                if mails['statut']=='supprimé' or mails['statut'] == 'removed':
                    stat = Statistiques(date= datetime.today().strftime('%Y-%m-%d'), actionFiltre=REFUSED)
                    mail = Mail.query.filter_by(id=mails['identifiant']).first()
                    db.session.add(stat)
                    db.session.delete(mail)
                if mails['statut']=='acheminé' or 'sent':
                    stat = Statistiques(date= datetime.today().strftime("%Y-%m-%d"), actionFiltre= ACCEPTED)
                    db.session.add(stat)
                    # mail.statut = ACCEPTED
                    db.session.delete(mail)
                if mails['statut']=='en attente' or 'pending':
                    stat = Statistiques(date= datetime.today().strftime("%Y-%m-%d"), actionFiltre= UNDECIDED)
                    db.session.add(stat)
                    # mail.statut = UNDECIDED
            db.session.commit()
            return render_template("consultmails.html", )
    except IndexError:
        abort(404)
        
@app.route('/consultexp/', methods=['GET', 'POST'])
def consultexp():
    try:
        if 'mail' not in session:
            flash(gettext("Pas de compte connecté"), "deconnecte") 
            return redirect(url_for("login"))
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id)
        t = dict()
        for exp in expediteurs:
            mails = Mail.query.filter_by(expediteur_id=exp.id).count()
            t[exp.mail] = mails
        # mails = Mail.query.filter_by(expediteur_id = expediteurs.id)
        if request.method == "POST":
            expediteur = request.form.get('mail')
            if expediteur != None:
                return redirect(url_for("consultmailsexp", expediteur=expediteur))
        return render_template("consultexp.html", mail=session['mail'], users=users, expediteurs=expediteurs, t=t)
    except IndexError:
        abort(404)
	

@app.route('/api/modifexp/', methods=['GET', 'POST'])
def modifexp():
    try:
        users = Utilisateur.query.filter_by(mail=session['mail']).first()
        expediteurs = Expediteur.query.filter_by(utilisateur_id=users.id)
        t = dict()
        for exp in expediteurs:
            mails = Mail.query.filter_by(expediteur_id=exp.id).count()
            t[exp.mail] = mails
        if request.method == "POST":
            tab = request.get_json(force=true)['paramName'] 
            for exps in tab: 
                exp = Expediteur.query.filter_by(mail=exps['mail']).first()
                if exps['statut']=='1':
                    stat = Statistiques(date= datetime.today().strftime('%Y-%m-%d'), actionFiltre=1)
                    db.session.add(stat)
                    exp.statut = ACCEPTED
                    # on va acheminer ses mails
                    # mails = Mail.query.filter_by(expediteur_id=exp.id).all()
                    # for mail in mails:
                        # stat = Statistiques(date= today.strftime("%Y-%m-%d"), actionFiltre= ACCEPTED)
                        # db.session.add(stat)
                        # mail.statut = ACCEPTED
                else:
                    if exps['statut']=='2':
                        stat = Statistiques(date= datetime.today().strftime('%Y-%m-%d'), actionFiltre=REFUSED)
                        exp.statut = REFUSED
                        db.session.add(stat)
                        # on va supprimer ses mails 
                        # mails = Mail.query.filter_by(expediteur_id=exp.id).all()
                        # for mail in mails:
                            # stat = Statistiques(date= today.strftime("%Y-%m-%d"), actionFiltre= REFUSED)
                            # db.session.add(stat)
                            # mail.statut = ACCEPTED
                    else:
                        stat = Statistiques(date= datetime.today().strftime('%Y-%m-%d'), actionFiltre=UNDECIDED)
                        db.session.add(stat)
                        exp.statut = UNDECIDED
                        # on va mettre en attente ses mails 
                        # mails = Mail.query.filter_by(expediteur_id=exp.id).all()
                        # for mail in mails:
                            # stat = Statistiques(date= today.strftime("%Y-%m-%d"), actionFiltre= REFUSED)
                            # db.session.add(stat)
                            # mail.statut = ACCEPTED
            db.session.commit()
            return render_template("consultexp.html", mail=session['mail'], users=users, expediteurs=expediteurs, t=t)
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

# permet de lancer l'appli
if __name__ == "__main__":
    app.run(debug=True)
    db.init_app(app)
    db.create_all()
