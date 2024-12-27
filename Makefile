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

run-api: setup
	( . ./devsetup; python main.py run_flask_app )

run-watchall: setup
	( . ./devsetup; python main.py update_all_installations )

run-watchme: setup
	( . ./devsetup; python main.py update_one_inbox 1vxqiy2eZSdkbOrNkNhbeomknwxSiK77E )
