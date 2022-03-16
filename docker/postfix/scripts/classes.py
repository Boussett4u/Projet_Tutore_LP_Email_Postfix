#!/usr/bin/python3
#coding: utf-8

import os, sys, smtplib, getopt, subprocess, fileinput, email
from datetime import datetime  
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Importation des variables du docker-compose
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_ip = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

#Configuration pour utiliser flask et SQLAlchemy               
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://"+db_user+":"+db_password+"@"+db_ip+":"+db_port+"/"+db_name)
db = SQLAlchemy(app)

#Création des classes correspondant aux tables de la base de données (utilisé aussi pour la création de la base en phase de test)

class Utilisateur(db.Model):
        #Définition des colonnes
        id = db.Column(db.Integer, primary_key=True)
        nom = db.Column(db.String(250), unique=True, nullable=True)
        mdp = db.Column(db.String(250), unique=False, nullable=False)
        admin = db.Column(db.Boolean, default=False)
        mail = db.Column(db.String(250), unique=False, nullable=False)

        #Constructeur
        def __init__(self, nom, mdp, admin, mail):
                self.nom = nom
                self.mdp = mdp
                self.admin = admin
                self.mail = mail
        
class Expediteur(db.Model):
        #Définition des colonnes
        id = db.Column(db.Integer, primary_key=True)
        mail = db.Column(db.String(250), unique=True, nullable=False)
        utilisateur_id = db.Column(db.ForeignKey(Utilisateur.id), nullable=False)
        statut = db.Column(db.Integer, unique=False, nullable=False, default=3)
        #statut : 1 validé, 2 refusé, 3 en attente
        token = db.Column(db.String(250), unique=True, nullable=False)

        #Constructeur
        def __init__(self, mail, utilisateur_id, statut, token): 
                self.mail = mail
                self.utilisateur_id = utilisateur_id
                self.statut = statut
                self.token = token

class Mail(db.Model):
        #Définition des colonnes
        id = db.Column(db.Integer, primary_key=True)
        id_mail_postfix = db.Column(db.String(250), unique=True, nullable=False)
        expediteur_id = db.Column(db.ForeignKey(Expediteur.id), nullable=False)
        date = db.Column(db.DateTime, nullable=False)

        #Constructeur
        def __init__(self,id_mail_postfix, expediteur_id):
                self.id_mail_postfix = id_mail_postfix
                self.expediteur_id = expediteur_id
                self.date = datetime.now()


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
                

                
db.create_all()
