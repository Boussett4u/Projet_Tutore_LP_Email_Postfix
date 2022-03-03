#!/bin/bash


# Génération de la base de données avec le scripts python
# Ne se génere pas !!!! S'éxecute avant le montage des volumes ? 
/scripts/classes.py


# Lien symbolique pour le script filtre.py du master.cf
mkdir /home/testfilter/filtre
ln -s /scrits/filtre/filtre.py /home/testfilter/filtre/filtre.py


# Permission d'accès au dossier correspondant depuis la machine hôte
chmod -R 777 /etc/prostfix
chmod -R 777 /home
chmod -R 777 /var/spool
chmod -R 777 /scripts


# Temporaire
. env/bin/activate
pip install flask flask-restplus Flask-reCaptcha flask-sqlalchemy psycopg2-binary sqlalchemy-utils Flask-Migrate flask-bcrypt Flask-WTF Flask-Babel Flask pytest \


# Sleep pour que le docker soit actif
sleep 100000000