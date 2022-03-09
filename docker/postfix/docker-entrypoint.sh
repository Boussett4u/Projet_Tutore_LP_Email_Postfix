#!/bin/bash

# Export des variables du docker-compose 
export DB_IP
export DB_USER
export DB_NAME
export DB_PORT
export DB_PASSWORD
export POSTFIX_DOMAIN

# Génération de la base de données avec le scripts python
/scripts/classes.py

# Initialisation de /etc/postfix/transport
rm /etc/postfix/transport
touch /etc/postfix/transport
for (( i = 1 ; i < $(echo `expr $(echo -n $POSTFIX_DOMAIN | tr -d [:alnum:]\@\.\: | wc -c) + 2`) ; i++)) do
    echo $POSTFIX_DOMAIN | awk -F ";" '{print $'$i'}' | sed -e 's/:/\trelay:/g' | sed -e 's/$/:587/g' >> /etc/postfix/transport
done

# Lien symbolique pour le script filtre.py du master.cf
mkdir /home/testfilter/filtre
ln -s /scrits/filtre/filtre.py /home/testfilter/filtre/filtre.py

# Permission d'accès au dossier correspondant depuis la machine hôte
chmod -R 777 /etc/prostfix
chmod -R 777 /home
chmod -R 777 /var/spool
chmod -R 777 /scripts

# Sleep pour que le docker soit actif
sleep 100000000