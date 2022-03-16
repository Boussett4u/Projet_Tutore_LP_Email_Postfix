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
from fonctionsCommunes import envoyerLien, ajouterMail, ajouterExpediteur, ajouterStat, verifSiTokenIdentique

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

#Fonction permettant d'envoyer un lien de validation a l'expéditeur dont le statut est en attente
# def envoyerLien(expediteur, mailValidation, destinataire):

#         #On récupère le token de l'expediteur
#         expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()
        
#         #Envoi d'un mail à l'expéditeur avec le lien de validation
#         smtp = smtplib.SMTP("localhost")
#         smtp.sendmail("reject@localhost", [expediteur], "From: no-reply@localhost\nTo:{0}\n{1}http://127.0.0.1:5000/validation/{2}".format(destinataire, mailValidation, expediteur_bdd.token))

def miseQuarantaine(mail_id, message):

        #Mise en quarantaine du message dans un répertoire spécifique
        mailFichier = open("/home/testfiltre/quarantaine/{0}".format(mail_id), "a")
        mailFichier.write(message)
        mailFichier.close()

# #Fonction permettant d'ajouter un nouveau mail dans la table
# def ajouterMail(expediteur, mail_id):
#         infoExpediteur = Expediteur.query.filter_by(mail=expediteur).first()
#         nouveauMail = Mail (mail_id, infoExpediteur.id, datetime.now())
#         db.session.add(nouveauMail)
#         db.session.commit()

# #Fonction pour ajouter un expéditeur
# def ajouterExpediteur(destinataire, expediteur):
#         #calcul de la date pour le token
#         date=datetime.now()

#         #Ajout des informations
#         infoDestinataire = Utilisateur.query.filter_by(mail=destinataire).first()
#         nouvelExpediteur = Expediteur(expediteur, infoDestinataire.id, 3, hashlib.md5(("VALIDATE"+date.strftime("%m/%d/%Y")+expediteur).encode('utf-8')).hexdigest())
#         db.session.add(nouvelExpediteur)
#         db.session.commit()

# #Fonction pour ajouter une entrée dans la table statistiques
# def ajouterStat(statut):
#         if statut==1:
#                 nouvelleStat = Statistiques(datetime.now(), 1)
#         elif statut==2:
#                 nouvelleStat = Statistiques(datetime.now(), 2)
#         else:
#                 nouvelleStat = Statistiques(datetime.now(), 3)
#         db.session.add(nouvelleStat)
#         db.session.commit()

        

# #Fonction permettant de verifier si le token existe
# def verifSiTokenIdentique(expediteur, destinataire):
#         date=datetime.now()
#         tokenCalcule=hashlib.md5(("VALIDATE"+date.strftime("%m/%d/%Y")+expediteur).encode('utf-8')).hexdigest()
#         destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()
#         tokenExpediteur=Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).first()

#         syslog.syslog(syslog.LOG_INFO, '{0}'.format(tokenCalcule))
#         if tokenCalcule==tokenExpediteur.token:
#                 return True
#         else:
#                 return False
                
                
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
        
