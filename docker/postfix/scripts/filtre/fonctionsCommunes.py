#!/usr/bin/python3
#coding: utf-8


#Importation des variables du docker-compose
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

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
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://{0}:{1}@{2}:{3}/{4}".format(db_user, db_password, db_host, db_port, db_name))
db = SQLAlchemy(app)



#Fonction permettant d'envoyer un lien de validation a l'expéditeur dont le statut est en attente
def envoyerLien(expediteur, mailValidation, destinataire):

        #Récupération des informations destinataires
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()

    
        #On récupère le token de l'expediteur
        expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()
        
        #Envoi d'un mail à l'expéditeur avec le lien de validation
        smtp = smtplib.SMTP("localhost")
        smtp.sendmail([destinataire], [expediteur], "From: no-reply@localhost\nTo:{0}\n{1}http://127.0.0.1:5000/validation/{2}".format(destinataire, mailValidation, expediteur_bdd.token))

        
#Fonction permettant d'ajouter un nouveau mail dans la table
def ajouterMail(expediteur, mail_id):
        infoExpediteur = Expediteur.query.filter_by(mail=expediteur).first()
        nouveauMail = Mail (mail_id, infoExpediteur.id, datetime.now())
        db.session.add(nouveauMail)
        db.session.commit()


#Fonction pour ajouter un expéditeur
def ajouterExpediteur(destinataire, expediteur):
        #calcul de la date pour le token
        date=datetime.now()

        #Ajout des informations
        infoDestinataire = Utilisateur.query.filter_by(mail=destinataire).first()
        nouvelExpediteur = Expediteur(expediteur, infoDestinataire.id, 3, hashlib.md5(("VALIDATE"+date.strftime("%m/%d/%Y")+expediteur).encode('utf-8')).hexdigest())
        db.session.add(nouvelExpediteur)
        db.session.commit()

#Fonction pour ajouter une entrée dans la table statistiques
def ajouterStat(statut):
        if statut==1:
                nouvelleStat = Statistiques(datetime.now(), 1)
        elif statut==2:
                nouvelleStat = Statistiques(datetime.now(), 2)
        else:
                nouvelleStat = Statistiques(datetime.now(), 3)
        db.session.add(nouvelleStat)
        db.session.commit()

#Fonction permettant de verifier si le token existe
def verifSiTokenIdentique(expediteur, destinataire):
        date=datetime.now()
        tokenCalcule=  hashlib.md5(("VALIDATE"+date.strftime("%m/%d/%Y")+expediteur).encode('utf-8')).hexdigest()
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()
        tokenExpediteur=Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).first()

        if tokenCalcule==tokenExpediteur.token:
                return True
        else:
                return False
                
