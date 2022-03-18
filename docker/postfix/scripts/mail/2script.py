#!/usr/bin/python3
#coding utf-8

import smtplib, sys


#On créé un objet smtp qui va permettre d'envoyer les mails
smtp = smtplib.SMTP("localhost") #Le paramètre est l'adresse du MTA a utiliser

#Ensuite, on peut envoyer le mail
smtp.sendmail(sys.argv[1], [sys.argv[2]], "From: root\nTo: <destinataire>\nSubject: Test de mail\n\n <message ici !!!!!!!!!!!>")
