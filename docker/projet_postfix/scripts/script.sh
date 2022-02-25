#!/bin/bash

# Ajout python

apt update
apt install -y iproute2
apt install -y python
apt install -y python3-flask
apt install -y python3-flask-sqlalchemy
apt install -y python3-psycopg2
apt install -y postgresql-client


# Intégration des users de test
useradd -m paul
useradd -m reject
useradd -m hold
useradd -m filter
useradd -m defer
useradd -m testfilter
mkdir /home/testfilter/quarantaine

# Lien symbolique pour le script filtre.py du master.cf
mkdir /home/testfilter/filtre
ln -s /scrits/filtre/filtre.py /home/testfilter/filtre/filtre.py

# Permission d'accès au dossier correspondant depuis la machine hôte
chmod -R 777 /etc/prostfix
chmod -R 777 /home
chmod -R 777 /var/spool
chmod -R 777 /scripts

# Génération de la base de données avec le scripts python
./scripts/classes.py

# Sleep pour que le docker soit actif
sleep 1000000
