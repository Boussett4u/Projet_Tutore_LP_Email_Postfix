#!/bin/bash
# Mise à jour
apt update
# Permission d'accès au dossier postgres (Projet*/docker/projet/database)
chmod -R 777 /var/lib/postgresql