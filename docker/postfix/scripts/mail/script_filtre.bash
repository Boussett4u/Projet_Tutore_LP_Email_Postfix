#!/bin/sh
 
# Répertoires
INSPECT_DIR=/var/spool/filter
SENDMAIL="/usr/sbin/sendmail -G -i" # n'employer JAMAIS "-t" ici
 
# Codes de retour issus de <sysexits.h>
EX_TEMPFAIL=75
EX_UNAVAILABLE=69
 
# Nettoyage lors en sortant ou lors d'une interruption
trap "rm -f in.$$" 0 1 2 3 15
 
# Démarrage du processus.
cd $INSPECT_DIR || {
	echo $INSPECT_DIR n\'existe pas; 
	exit $EX_TEMPFAIL; }

	cat >in.$$ || { 
		echo Impossible de saugarder le message dans un fichier; exit $EX_TEMPFAIL; }

# Ecrivez votre filtrage de contenu ici:
echo "AAAAAAAAAAAAAA" >> in.$$ || {
	echo Contenu de message content rejet; exit $EX_UNAVAILABLE; }
 
	$SENDMAIL "$@" <in.$$
 
exit $?
