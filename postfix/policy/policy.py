#!/usr/bin/python3
#coding: utf-8

#On récupère les modules nécessaires
import os, sys, smtplib, getopt, subprocess, fileinput, email, hashlib, syslog
from datetime import datetime

#Ici ce qui concerne l'ORM
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Ici ce qui concerne les classes créées dans le fichiers classes.py
from classes import Utilisateur, db, Expediteur, Mail, Statistiques



#Configuration pour utiliser flask et SQLAlchemy               
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postfix:postfix@localhost:5432/postfix'
db = SQLAlchemy(app)

#Création des classes correspondant aux tables de la base de données (utilisé aussi pour la création de la base en phase de test)

class Utilisateur(db.Model):
        #Définition des colonnes
        id = db.Column(db.Integer, primary_key=True)
        identifiant = db.Column(db.String(250), unique=True, nullable=False)
        nom = db.Column(db.String(250), unique=True, nullable=True)
        mdp = db.Column(db.String(250), unique=False, nullable=False)
        admin = db.Column(db.Boolean, default=False)
        mail = db.Column(db.String(250), unique=False, nullable=False)

        #Constructeur
        def __init__(self, identifiant, nom, mdp, admin, mail):
                self.identifiant = identifiant
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
        def __init__(self,id_mail_postfix, expediteur_id, date):
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
 

# #Récupération du message
# message=""
# for line in sys.stdin:
#         message += line

message=""
while 1:
    line = sys.stdin.readline()
    if line=='\n':
        break
    else:
        message+=line

parametre={}
# fichier = open("/home/testfiltre/filtre/test.txt", "r")
# for ligne in fichier:
#         resu = line.split("=")
#         parametre[resu[0]] = resu[1]  
# fichier.close()


# while 1:
#     line = sys.stdin.readline()
#     if line=='\n':
#         break
#     else:
#         resu = line.split("=")
#         parametre[resu[0]] = resu[1]  
 
        



fichier = open("/home/testfiltre/filtre/test.txt", "a")
fichier.write(message)
fichier.close()

# fichier = open("/home/testfiltre/filtre/test2.txt", "a")
# fichier.write(parametre["recipient"])
# fichier.close()

        
print("action=hold \n")
