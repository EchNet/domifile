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

build: setup
	(. ./.env; gcloud builds submit --tag gcr.io/your_project_id/domifile-processor)

deploy: build
	(. ./.env; gcloud run deploy domifile-processor --image gcr.io/your_project_id/domifile-processor --platform managed --region us-central1 --allow-unauthenticated)
