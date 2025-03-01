# Make commands for development
# 
# `make setup` install required Python modules.

PIP=pip
PYTHON=python

setup: requirements.flag

requirements.txt: requirements.in
	$(PIP) install -r requirements.in
	echo "# GENERATED FROM requirements.in.  DO NOT EDIT DIRECTLY." > requirements.txt
	$(PIP) freeze >> requirements.txt

requirements.flag: requirements.txt
	$(PIP) install -r requirements.txt
	touch requirements.flag

run: setup
	flask run

test: setup
	pytest

ngrok:
	ngrok http 8080
