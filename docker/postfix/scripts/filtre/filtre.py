#!/usr/bin/python3
#coding: utf-8

#On récupère les modules nécessaires
import os, sys, smtplib, getopt, subprocess, fileinput, email, hashlib, syslog
from datetime import datetime

#Ici ce qui concerne l'ORM
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Ici ce qui concerne les classes créées dans le fichiers classes.py
sys.path.append("/scripts/")
from classes import Utilisateur, db, Expediteur, Mail, Statistiques
from fonctionsCommunes import envoyerLien, ajouterMail, ajouterExpediteur, ajouterStat, verifSiTokenIdentique

#Importation des variables du docker-compose
db_user = os.getenv('DB_USER')
db_pwd = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

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
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://"+db_user+":"+db_pwd+"@"+db_host+":"+db_port+"/"+db_name)
db = SQLAlchemy(app)
                
#Actions du filtre

#Récupération des paramètres transmis par Postfix et spécifiés dans master.cf
destinataire = options["-d"]
expediteur = options["-e"]
mail_id = options["-q"]

#Préparation du mail de validation
mailValidation="Sujet : validation expediteur \n Veuillez cliquer sur ce lien et valider le CAPTCHA  : "

#Récupération du message
message=""
for line in sys.stdin:
        message += line

#Fonctione permettant la mise en quarantaine
def miseQuarantaine(mail_id, message):
        #Mise en quarantaine du message dans un répertoire spécifique
        mailFichier = open("/home/testfiltre/quarantaine/{0}".format(mail_id), "a")
        mailFichier.write(message)
        mailFichier.close()
 
#Traitement en fonction de l'expéditeur et de son statut

#Transmission des logs a rsyslog
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_MAIL)

#Vérification de l'existence du destinataire dans la table
destinataire_existe = Utilisateur.query.filter_by(mail=destinataire).count()

#S'il existe
if destinataire_existe > 0:

        syslog.syslog(syslog.LOG_INFO, 'Le destinataire {0} est protege'.format(destinataire))

        #Récupération de ses informations
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()

        #Vérification de l'expéditeur, est-il déjà dans la table et associé à ce destinataire ?
        expediteur_existe = Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).count()

        #Si oui
        if expediteur_existe > 0:

                #Récupération de l'objet de la base correspondant à cet expéditeur dans une variable
                expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()

                #En fonction du statut
        
                #Si accepté
                if expediteur_bdd.statut==1:

                        #Information destinée aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur {0} est valide -> mail {1} livre'.format(expediteur, mail_id))
                
                        #Envoi du mail sans contrôle particulier
                        sendmail = os.popen("/usr/lib/sendmail {0}".format(destinataire), "w")
                        sendmail.write(message)

                        #Ajout d'une entrée dans la table statistiques
                        ajouterStat(1)
               
                #Si refusé        
                elif expediteur_bdd.statut==2:

                        #Informations destinées aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur {0} bloque -> mail {1} refuse'.format(expediteur, mail_id))    
                
                        #Ajoute d'une entrée dans la table statistiques
                        ajouterStat(2)

                        #Envoi du code d'erreur 69 qui permet a postfix de retourner le message à l'expéditeur comme non-livrable
                        EX_UNVALIABLE=69
                        sys.exit(EX_UNVALIABLE)

                #Si en attente
                else:

                        #Vérification permettant de savoir si un lien doit être envoyé
                        if verifSiTokenIdentique(expediteur, destinataire)!=True:
                                envoyerLien(expediteur,mailValidation, destinataire)
                                #Informations destinées aux logs
                                syslog.syslog(syslog.LOG_INFO, 'Expediteur {0} en attente -> mail {1} en quarantaine + validation envoyee'.format(expediteur, mail_id))
                        else:
                                #Informations destinées aux logs
                                syslog.syslog(syslog.LOG_INFO, 'Expediteur {0} en attente -> mail {1} en quarantaine - validation deja envoyee - attente de validation par l\'expediteur'.format(expediteur,mail_id))
            

                        #Mise en quarantaine du mail
                        miseQuarantaine(mail_id, message)

                        #Enregistrement du mail dans la base pour pouvoir le retrouver :
                        ajouterMail(expediteur, mail_id)

                        #Ajout d'une entrée dans la table statistiques
                        ajouterStat(3)

        #Cas où l'expéditeur n'existe pas dans la table Expediteur                
        else:

                #Informations destinées aux logs
                syslog.syslog(syslog.LOG_INFO, 'L\'expediteur {0} n\'est pas reference -> mail {1} en quarantaine + validation envoyee'.format(expediteur, mail_id))
        
                #Ajout de l'expéditeur inconnu dans la base avec le statut en attente
                ajouterExpediteur(destinataire, expediteur)

                #Ajout du mail correspondant dans la table mail
                ajouterMail(expediteur, mail_id)

                #Fonction permettant de générer le lien et l'envoyer
                envoyerLien(expediteur, mailValidation, destinataire)

                #Mise en quarantaine du mail
                miseQuarantaine(mail_id, message)

                #Ajout d'une entrée dans la table statistique
                ajouterStat(3)


else:
        syslog.syslog(syslog.LOG_INFO, 'Le destinataire {0} est introuvable')
        
