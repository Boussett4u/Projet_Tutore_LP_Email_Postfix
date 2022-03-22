#!/bin/bash

# Export des variables du docker-compose 
export DB_HOST
export DB_USER
export DB_NAME
export DB_PORT
export DB_PASSWORD
export POSTFIX_DOMAIN
MAILNAME=${MAILNAME:-mio.example.com}
export MAILNAME
export MIO_METHOD=${MIO_METHOD:-policy}

echo -e "export DB_HOST='${DB_HOST}'\nexport DB_USER='${DB_USER}'\nexport DB_NAME='${DB_NAME}'\nexport DB_PORT='${DB_PORT}'\nexport DB_PASSWORD='${DB_PASSWORD}'" >/scripts/filtre/conf.env

# Génération de la base de données avec le scripts python
/scripts/classes.py

# Initialisation de /etc/postfix/transport
if [ -e /etc/postfix/transport ]; then
  rm /etc/postfix/transport
fi

touch /etc/postfix/transport

echo $MAILNAME > /etc/mailname
postconf -e "myhostname = ${MAILNAME}"
postconf -e "mydestination = ${MAILNAME}, localhost.localdomain, localhost"
postconf -e "transport_maps = hash:/etc/postfix/transport"

case $MIO_METHOD in
  filter)
    echo "Configuration pour FILTER"
    postconf -e "smtpd_recipient_restrictions = check_recipient_access pcre:/etc/postfix/access"
  ;;
  policy | *)
    echo "Configuration pour POLICY"
    postconf -e "smtpd_data_restrictions = permit_mynetworks reject_unauth_destination check_policy_service unix:private/policy"
    postconf -e "policy_time_limit = 3600"
    postconf -e "smtpd_policy_service_request_limit = 1"
    postconf -e "export_environment = TZ MAIL_CONFIG LANG DB_HOST DB_USER DB_PASSWORD DB_NAME DB_PORT"
    cp /etc/postfix/master.policy.cf /etc/postfix/master.cf
  ;;
esac

echo $POSTFIX_DOMAIN | tr ';' '\n' | sed -e 's/=/\trelay:/g'  >> /etc/postfix/transport
RELAY_DOMAINS=$(echo $POSTFIX_DOMAIN | sed -e 's/\([^=]\+\)[^;]*\(;\|$\)/\1 /g')
postconf -e "relay_domains = ${RELAY_DOMAINS}"

postmap /etc/postfix/transport
newaliases

# Lien symbolique pour le script filtre.py du master.cf
mkdir /home/testfilter/filtre
ln -s /scripts/filtre/filtre.py /home/testfilter/filtre/filtre.py
ln -s /scripts/filtre/policy.py /home/testfilter/filtre/policy.py

# Permission d'accès au dossier correspondant depuis la machine hôte
#chmod -R 777 /etc/postfix
#chmod -R 777 /home
#chmod -R 777 /var/spool
chmod  a+rx /scripts/*

# lancer rsyslog
/usr/sbin/rsyslogd
# lancer postfix
#/usr/lib/postfix/configure-instance.sh
/etc/init.d/postfix start
flask run
