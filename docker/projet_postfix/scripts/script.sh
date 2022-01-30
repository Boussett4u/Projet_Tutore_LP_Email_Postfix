#!/bin/bash

# Ajout python

apt update
apt install -y iproute2
apt install -y python
apt install -y python3-flask
apt install -y python3-flask-sqlalchemy
apt install -y postgresql-client


# Intégration des users de test
useradd -m paul
useradd -m reject
useradd -m hold
useradd -m filter
useradd -m defer
useradd -m testfilter
mkdir /home/testfilter/quarantaine

# Permission d'accès au dossier correspondant depuis la machine hôte
chmod -R 777 /etc/prostfix
chmod -R 777 /home
chmod -R 777 /var/spool

# Sleep pour que le docker soit actif
sleep 1000000
