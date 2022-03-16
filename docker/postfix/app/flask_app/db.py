#!/usr/bin/python3
#coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from config import bdd_uri as settings

# creation d'une instance de flask
app = Flask(__name__)

# On donne la chaine de connexion pour la base de donnees
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(pguser)s:\
%(pgpasswd)s@%(pghost)s:%(pgport)s/%(pgdb)s' % settings
# On instancie un objet de type orm avec la chaine de connection
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# On instancie le modele permettant de formaliser les donnees pour les envoyer a la table Utilisateurs
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(250), unique=True, nullable=True)
    mail = db.Column(db.String(250), unique=False, nullable=False)
    mdp = db.Column(db.String(250), unique=False, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    def __init__(self, nom, mail, mdp, admin):
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
class Statistiques(db.Model):
        #Définition des colonnes
        id = db.Column(db.Integer, primary_key=True)
        date = db.Column(db.DateTime, nullable=False)
        #1 = accepté, 2 = rejeté, 3 = en attente
        actionFiltre = db.Column(db.Integer, nullable=False)
        #Constructeur
        def __init__(self, date, actionFiltre):
                self.date = date
                self.actionFiltre = actionFiltre
