#!/bin/sh
sudo apt update
sudo apt -y upgrade
sudo apt install -y python3-pip
sudo apt install -y python3-flask
sudo apt install -y python-pip
pip3 install package_name
python3 -m pip install --user --upgrade pip
sudo apt install -y build-essential libssl-dev libffi-dev python-dev
sudo apt install -y python3-venv
. env/bin/activate
pip install flask
pip install flask-restplus
pip install Flask-reCaptcha
pip install flask-sqlalchemy
pip install psycopg2-binary
pip install sqlalchemy-utils
pip install Flask-Migrate
pip install flask-bcrypt # chiffrement mot de passe
pip install Flask-WTF
pip install Flask-Babel
pip install Flask
#cd /env/flask_app
#flask db init
#flask db migrate
#flask db upgrade
pip install pytest
