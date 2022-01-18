#!/bin/sh
sudo apt update
sudo apt -y upgrade
sudo apt install -y python3-pip
sudo apt install -y python3-flask
pip3 install package_name
sudo apt install -y build-essential libssl-dev libffi-dev python-dev
sudo apt install -y python3-venv
. env/bin/activate
pip install flask
pip install flask-restplus