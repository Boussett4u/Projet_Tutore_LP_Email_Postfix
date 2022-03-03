#!/bin/bash
# Mise à jour
apt update
apt install -y iproute2
# Permission d'accès au dossier postgres (Projet*/docker/projet/database)
chmod -R 777 /var/lib/postgresql