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


#Récupération des arguments
#e: = expediteur, d: destinataire, q: id_mail
try:
        opts, args = getopt.getopt(sys.argv[1:], 'e:d:q:')
#message d'erreur si l'argument n'est pas bon
except:
        print("erreur d'argument")
        sys.exit(1)

#Tableau avec en clé l'option et en valeur le paramètre correspondant
#Il permet de récupérer le paramètre correspondant à l'option indiquée, plutôt de le récupérer en tenant compte de sa position
#il s'agit d'un hash sous forme clé valeur, ce qui permet de toujours avoir le destinataire en faisant options[-d]
options = {}
for opt, arg in opts:
        options[opt]=arg

#Configuration pour utiliser flask et SQLAlchemy               
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postfix:postfix@localhost:5432/postfix'
db = SQLAlchemy(app)

#Création des classes correspondant aux tables de la base de données (utilisé aussi pour la création de la base en phase de test)

# class Utilisateur(db.Model):
#         #Définition des colonnes
#         id = db.Column(db.Integer, primary_key=True)
#         identifiant = db.Column(db.String(250), unique=True, nullable=False)
#         nom = db.Column(db.String(250), unique=True, nullable=True)
#         mdp = db.Column(db.String(250), unique=False, nullable=False)
#         admin = db.Column(db.Boolean, default=False)
#         mail = db.Column(db.String(250), unique=False, nullable=False)

#         #Constructeur
#         def __init__(self, identifiant, nom, mdp, admin, mail):
#                 self.identifiant = identifiant
#                 self.nom = nom
#                 self.mdp = mdp
#                 self.admin = admin
#                 self.mail = mail
        
# class Expediteur(db.Model):
#         #Définition des colonnes
#         id = db.Column(db.Integer, primary_key=True)
#         mail = db.Column(db.String(250), unique=True, nullable=False)
#         utilisateur_id = db.Column(db.ForeignKey(Utilisateur.id), nullable=False)
#         statut = db.Column(db.Integer, unique=False, nullable=False, default=3)
#         #statut : 1 validé, 2 refusé, 3 en attente
#         token = db.Column(db.String(250), unique=True, nullable=False)

        
#         #Constructeur
#         def __init__(self, mail, utilisateur_id, statut, token): 
#                 self.mail = mail
#                 self.utilisateur_id = utilisateur_id
#                 self.statut = statut
#                 self.token = token

# class Mail(db.Model):
#         #Définition des colonnes
#         id = db.Column(db.Integer, primary_key=True)
#         id_mail_postfix = db.Column(db.String(250), unique=True, nullable=False)
#         expediteur_id = db.Column(db.ForeignKey(Expediteur.id), nullable=False)
#         date = db.Column(db.DateTime, nullable=False)

#         #Constructeur
#         def __init__(self,id_mail_postfix, expediteur_id, date):
#                 self.id_mail_postfix = id_mail_postfix
#                 self.expediteur_id = expediteur_id
#                 self.date = date

# class Statistiques(db.Model):
#         #Définition des colonnes
#         id = db.Column(db.Integer, primary_key=True)
#         date = db.Column(db.DateTime, nullable=False)
#         #1 = accepté, 2 = rejeté, 3 = en attente
#         actionFiltre = db.Column(db.Integer, nullable=False)
        
#         #Constructeur
#         def __init__(self, date, actionFiltre):
#                 self.date = date
#                 self.actionFiltre = actionFiltre
                
#Actions du filtre

#Récupération des paramètres transmis par Postfix et spécifiés dans master.cf
destinataire = options["-d"]
expediteur = options["-e"]
mail_id = options["-q"]

#Préparation du mail de validation
mailValidation="Subjet : validation expediteur \n Veuillez cliquer sur ce lien et valider le CAPTCHA  : "

#Récupération du message
message=""
for line in sys.stdin:
        message += line

#Fonction permettant d'envoyer un lien de validation a l'expéditeur dont le statut est en attente, et de mettre le mail en quarantaine (en queue hold)
def envoyerLien(expediteur, mail_id, message, mailValidation, destinataire):

        #On récupère le token de l'expediteur
        expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()
        
        #Envoi d'un mail à l'expéditeur avec le lien de validation
        smtp = smtplib.SMTP("localhost")
        smtp.sendmail("reject@localhost", [expediteur], "From: no-reply@localhost\nTo:{0}\n{1}http://127.0.0.1:5000/validation/{2}".format(destinataire, mailValidation, expediteur_bdd.token))

        #Mise en quarantaine du message dans un répertoire spécifique
        mailFichier = open("/home/testfiltre/quarantaine/{0}".format(mail_id), "a")
        mailFichier.write(message)
        mailFichier.close()

#Fonction permettant d'ajouter un nouveau mail dans la table
def ajouterMail(expediteur, mail_id):
        infoExpediteur = Expediteur.query.filter_by(mail=expediteur).first()
        nouveauMail = Mail (mail_id, infoExpediteur.id)
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
                
                
#Traitement en fonction de l'expéditeur et de son statut


#Transmission des logs a rsyslog
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_MAIL)

#Vérification de l'existence du destinataire dans la table
destinataire_existe = Utilisateur.query.filter_by(mail=destinataire).count()

#S'il existe
if destinataire_existe > 0:

        #Récupération de ses informations
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()

        #Vérification de l'expéditeur, est-il déjà dans la table et associé à ce destinataire ?
        expediteur_existe = Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).count()

        #Si oui
        if expediteur_existe > 0:

                #Info pour le log
                syslog.syslog(syslog.LOG_INFO, 'L\'expediteur existe - Verification de son statut')

                #si oui, récupération de l'objet de la base correspondant à cet expéditeur dans une variable
                expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()

                #En fonction du statut
        
                #Si accepté
                if expediteur_bdd.statut==1:

                        #Information destinée aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur connu et valide - Tranfert du mail au destinataire')
                
                        #Envoi du mail sans contrôle particulier
                        sendmail = os.popen("/usr/lib/sendmail {0}".format(destinataire), "w")
                        sendmail.write(message)

                        #Ajout d'une entrée dans la table statistiques
                        ajouterStat(1)
               
                #Si refusé        
                elif expediteur_bdd.statut==2:

                        #Informations destinées aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur refuse - Mail retourne a l\'expediteur')      
                
                        #Ajoute d'une entrée dans la table statistiques
                        ajouterStat(2)

                        #Envoi du code d'erreur 69 qui permet a postfix de retourner le message à l'expéditeur comme non-livrable
                        EX_UNVALIABLE=69
                        sys.exit(EX_UNVALIABLE)
                
                else:
                        #Si en attente

                        #Informations destinées aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur en attente - Mail mis en quarantaine - Envoi d\'un lien de validation')
                
                        #Resprise de la fonction definie pour ce cas de figure, permettant de générer un lien et mettre en quarantaine
                        envoyerLien(expediteur, mail_id, message, mailValidation, destinataire)

                        #Enregistrement du mail dans la base pour pouvoir le retrouver :
                        ajouterMail(expediteur, mail_id)

                        #Ajout d'une entrée dans la table statistiques
                        ajouterStat(3)

        #Cas où l'expéditeur n'existe pas dans la table Expediteur                
        else:

                #Informations destinées aux logs
                syslog.syslog(syslog.LOG_INFO, 'Expediteur inconnu - Attribution du statut en attente - Mail mis en quarantaine - Envoi d\'un lien de validation')
        
                #Ajout de l'expéditeur inconnu dans la base avec le statut en attente
                ajouterExpediteur(destinataire, expediteur)

                #Ajout du mail correspondant dans la table mail
                ajouterMail(expediteur, mail_id)

                #Fonction permettant de générer le lien et envoyer en quarantaine le mail
                envoyerLien(expediteur, mail_id, message, mailValidation, destinataire)

                #Ajout d'une entrée dans la table statistique
                ajouterStat(3)


else:
        syslog.syslog(syslog.LOG_INFO, 'Destinataire inconnu')
