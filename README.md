# Projet_Tutore_LP

## Sujet
Le but de ce projet est de développer une solution facilement intégrable dans une chaîne de traitement de mail.

> **Le schéma général de fonctionnement est le suivant lors de l’arrivée d’un mail :**

* vérification du destinataire pour savoir si il doit être protégé
* vérification de l’expéditeur pour savoir si il a été validé
* si l’expéditeur n’est pas validé :
  * mettre le mail en quarantaine
  * envoyer un mail à l’expéditeur avec un lien de validation
  * lors de la consultation du lien de validation vérifier un captcha
  * si le captcha est ok -> valider l’expéditeur et acheminer le mail

> **Bien sûr il faudra développer une partie applicative web, afin de pouvoir réaliser les opération suivantes :**

* consulter les mails en quarantaine
* valider un expéditeur
 * bloquer un expéditeur
 * acheminer un/des mails sans validation
 * supprimer un/des mails

Le tout avec une authentification pour que chaque utilisateur ne puisse consulter QUE sa boite de quarantaine. Des super utilisateurs devront aussi pouvoir réaliser ces actions.

La partie mail se fera avec Postfix et la partie applicative préférentiellement en Python+Flask+Swagger et sera développée pour être déployée dans des conteneurs Docker.

## Installation de l'environnement

Il suffit de lancer le script installation.sh et dans le répertoire de app.py lancer les commandes

```bash
flask db init
flask db migrate
flask db upgrade
```






