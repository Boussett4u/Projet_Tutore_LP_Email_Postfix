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

message=""

#Récupération des paramètres 
parametres={}
while 1:
        line = sys.stdin.readline()
        if line=='\n':
                break
        else:
                #Construction d'une tableau clé valeur avec les paramètres
                message+=line
                resu = line.split("=")
                parametres[resu[0]] = resu[1]

destinataire = parametres["recipient"].strip()
expediteur = parametres["sender"].strip()
mail_id = parametres["queue_id"].strip()

#Préparation du mail de validation
mailValidation="Subjet : validation expediteur \n Veuillez cliquer sur ce lien et valider le CAPTCHA  : "


def envoyerLien(expediteur, mail_id, mailValidation, destinataire):
        #On récupère le token de l'expediteur
        expediteur_bdd = Expediteur.query.filter_by(mail=expediteur, utilisateur_id=destinataire_bdd.id).first()
        
        #Envoi d'un mail à l'expéditeur avec le lien de validation
        smtp = smtplib.SMTP("localhost")
        smtp.sendmail([destinataire], [expediteur], "From: no-reply@localhost\nTo:{0}\n{1}http://127.0.0.1:5000/validation/{2}".format(destinataire, mailValidation, expediteur_bdd.token))


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

#Voir pertinence de cette fonction car peut être que pas besoin
def verifSiTokenIdentique(expediteur, destinataire):
        date=datetime.now()
        tokenCalcule=  hashlib.md5(("VALIDATE"+date.strftime("%m/%d/%Y")+expediteur).encode('utf-8')).hexdigest()
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()
        tokenExpediteur=Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).first()
        if tokenCalcule==tokenExpediteur.token:
                return True
        else:
                return False
                
#Traitement en fonction de l'expéditeur et de son statut


#Transmission des logs a rsyslog
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_MAIL)

#Vérification de l'existence du destinataire dans la table
destinataire_existe = Utilisateur.query.filter_by(mail=destinataire).count()
                  

#S'il existe
if destinataire_existe > 0:

        syslog.syslog(syslog.LOG_INFO, 'Le destinataire existe')
        
        #Récupération de ses informations
        destinataire_bdd = Utilisateur.query.filter_by(mail=destinataire).first()

        #S'il n'est pas administrateur
        if destinataire_bdd.admin == False:

                syslog.syslog(syslog.LOG_INFO, 'Le destinataire est une adresse protegee')

                #Vérification de l'expéditeur, est-il déjà dans la table et associé à ce destinataire ?
                expediteur_existe = Expediteur.query.filter_by(mail=expediteur).filter_by(utilisateur_id=destinataire_bdd.id).count()

                #Si oui
                #if expediteur_existe > 0 and destinataire_bdd.admin == False:
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
                                #Ajout d'une entrée dans la table statistiques
                                ajouterStat(1)
                                #Le mail peut être envoyé
                                print("action=dunno \n")
                        

                                #Si refusé
                        elif expediteur_bdd.statut==2:
                                #Informations destinées aux logs
                                syslog.syslog(syslog.LOG_INFO, 'Expediteur refuse - Mail retourne a l\'expediteur')      

                                #Ajoute d'une entrée dans la table statistiques
                                ajouterStat(2)

                                #Le mail est rejeté
                                print("action=reject \n")

                        #Si en attente        
                        else:
                                #Informations destinées aux logs
                                syslog.syslog(syslog.LOG_INFO, 'Expediteur en attente - Mail mis en quarantaine')
                
                                #Reprise de la fonction definie pour ce cas de figure, permettant de générer un lien et mettre en quarantaine



                                #VERIFIER CA !!!!!!!!!!!!!!!!!!!!!!!!!!


                                
                                if verifSiTokenIdentique(expediteur, destinataire)!=True:
                                        envoyerLien(expediteur, mail_id, mailValidation, destinataire)
                                        syslog.syslog(syslog.LOG_INFO, 'Envoi d\'un lien de validation')
                                else:
                                        syslog.syslog(syslog.LOG_INFO, 'Mail de validation deja envoye')
            
                                #envoyerLien(expediteur, mail_id, mailValidation, destinataire)
                        
                        
                        
                                #Enregistrement du mail dans la base pour pouvoir le retrouver :
                                ajouterMail(expediteur, mail_id)

                                #Ajout d'une entrée dans la table statistiques
                                ajouterStat(3)

                                #Mise en file hold
                                print("action=hold \n")

                #Cas où l'expéditeur n'existe pas dans la table Expediteur
                else:
                        #Informations destinées aux logs
                        syslog.syslog(syslog.LOG_INFO, 'Expediteur inconnu - Attribution du statut en attente - Mail mis en quarantaine - Envoi d\'un lien de validation')

                        #Ajout de l'expéditeur inconnu dans la base avec le statut en attente
                        ajouterExpediteur(destinataire, expediteur)

                        #Ajout du mail correspondant dans la table mail
                        ajouterMail(expediteur, mail_id)

                        #Fonction permettant de générer le lien et envoyer en quarantaine le mail
                        envoyerLien(expediteur, mail_id, mailValidation, destinataire)

                        #Ajout d'une entrée dans la table statistique
                        ajouterStat(3)

                        #Mise en file hold
                        print("action=hold \n")

        else:
                
                syslog.syslog(syslog.LOG_INFO, 'Le destinataire est administrateur et non une adresse protegee - livraison du mail')
                print("action=dunno \n")
                                
else:
        syslog.syslog(syslog.LOG_INFO, 'Adresse non protegee - livraison du mail')
        print("action=dunno \n")


# fichier = open("/home/testfiltre/filtre/test.txt", "a")
# fichier.write(message)
# fichier.close()


# #Test pour voir si ça écrit bien le bon paramètre

# fichier = open("/home/testfiltre/filtre/test2.txt", "a")
# #fichier.write(parametres["recipient"])
# fichier.write("destinataire existe {0} destinataire {1} expediteur existe {2}, booleen{3}, retourToken{4}".format(destinataire_existe, destinataire, expediteur_existe, destinataire_bdd.admin, retourToken))

# fichier.close()


        
#print("action=dunno \n")
