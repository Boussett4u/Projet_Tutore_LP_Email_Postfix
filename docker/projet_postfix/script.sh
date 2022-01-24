#!/bin/bash

# Ajout du répertoire script et éxecution des scripts 
mkdir /scripts
cd /scripts
./scripts_filtre.bash
./2script.py

# Sleep pour que le docker soit actif
sleep 1000000
