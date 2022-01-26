#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE SEQUENCE IF NOT EXISTS utilisateur_id_seq;
  CREATE TABLE IF NOT EXISTS utilisateur(id INT NOT NULL DEFAULT nextval('utilisateur_id_seq'::regclass) PRIMARY KEY, identifiant VARCHAR(250) NOT NULL UNIQUE, nom VARCHAR(250) UNIQUE, mdp VARCHAR(250), administrateur BOOLEAN NOT NULL, mail VARCHAR(250) NOT NULL);
  CREATE SEQUENCE IF NOT EXISTS expediteur_id_seq;
  CREATE TABLE IF NOT EXISTS expediteur(id INT NOT NULL DEFAULT nextval('expediteur_id_seq'::regclass) PRIMARY KEY, mail VARCHAR(250) NOT NULL UNIQUE, utilisateur_id INT NOT NULL, statut INT NOT NULL, CONSTRAINT expediteur_utilisateur_id_fkey FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id));
  CREATE SEQUENCE IF NOT EXISTS mail_id_seq;
  CREATE TABLE IF NOT EXISTS mail(id INT NOT NULL DEFAULT nextval('mail_id_seq'::regclass) PRIMARY KEY, id_mail_postfix VARCHAR(250) NOT NULL UNIQUE, expediteur_id INT NOT NULL, CONSTRAINT mail_expediteur_id_fkey FOREIGN KEY (expediteur_id) REFERENCES expediteur(id));
EOSQL