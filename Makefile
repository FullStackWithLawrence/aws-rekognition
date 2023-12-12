SHELL := /bin/bash
PYTHON = python3
PIP = $(PYTHON) -m pip

.PHONY: env analyze init pre-commit requirements lint clean test build force-release publish-test publish-prod help


ifeq ($(OS),Windows_NT)
    ACTIVATE_VENV = venv\Scripts\activate
else
    ACTIVATE_VENV = source venv/bin/activate
endif

env:
	ifneq ("$(wildcard .env)","")
		include .env
	else
		$(shell echo -e "MAX_FACES_COUNT=10" >> .env)
		$(shell echo -e "FACE_DETECT_THRESHOLD=PLEASE-ADD-ME" >> .env)
		$(shell echo -e "FACE_DETECT_ATTRIBUTES=PLEASE-ADD-ME" >> .env)
		$(shell echo -e "QUALITY_FILTER=PLEASE-ADD-ME" >> .env)
		$(shell echo -e "TABLE_ID=gcp-starter" >> .env)
		$(shell echo -e "REGION=us-east-1" >> .env)
		$(shell echo -e "COLLECTION_ID=gcp-starter" >> .env)
		$(shell echo -e "DEBUG_MODE=True" >> .env)
	endif

# Default target executed when no arguments are given to make.
all: help

analyze:
	cloc . --exclude-ext=svg,json,zip --vcs=git

# -------------------------------------------------------------------------
# Initialize. create virtual environment and install requirements
# -------------------------------------------------------------------------
init:
	make clean && \
	npm install && npm init @eslint/config && \
	python3.11 -m venv venv && \
	$(ACTIVATE_VENV) && \
	pip install --upgrade pip && \
	make requirements

# -------------------------------------------------------------------------
# Install and run pre-commit hooks
# -------------------------------------------------------------------------
pre-commit:
	pre-commit install
	pre-commit run --all-files

# -------------------------------------------------------------------------
# Install requirements: Python, npm and pre-commit
# -------------------------------------------------------------------------
requirements:
	rm -rf .tox
	$(PIP) install --upgrade pip wheel
	$(PIP) install -r requirements.txt && \
	npm install && \
	pre-commit autoupdate
	make pre-commit

# -------------------------------------------------------------------------
# Run black and pre-commit hooks.
# includes prettier, isort, flake8, pylint, etc.
# -------------------------------------------------------------------------
lint:
	terraform fmt -recursive
	pre-commit run --all-files
	black ./terraform/python/

# -------------------------------------------------------------------------
# Destroy all build artifacts and Python temporary files
# -------------------------------------------------------------------------
clean:
	rm -rf ./terraform/.terraform venv .pytest_cache __pycache__ .pytest_cache node_modules && \
	rm -rf build dist aws-rekogition.egg-info

# -------------------------------------------------------------------------
# Run Python unit tests
# -------------------------------------------------------------------------
test:
	python -m unittest discover -s aws-rekogition/tests/ && \
	python -m setup_test

# -------------------------------------------------------------------------
# Force a new semantic release to be created in GitHub
# -------------------------------------------------------------------------
force-release:
	git commit -m "fix: force a new release" --allow-empty && git push

update:
	npm install -g npm
	npm install -g npm-check-updates
	ncu --upgrade --packageFile ./package.json
	npm update -g
	make init

build:
	@echo "Not implemented"

# -------------------------------------------------------------------------
# Generate help menu
# -------------------------------------------------------------------------
help:
	@echo '===================================================================='
	@echo 'init			- build virtual environment and install requirements'
	@echo 'analyze			- runs cloc report'
	@echo 'pre-commit		- install and configure pre-commit hooks'
	@echo 'requirements		- install Python, npm and pre-commit requirements'
	@echo 'lint			- run black and pre-commit hooks'
	@echo 'clean			- destroy all build artifacts'
	@echo 'test			- run Python unit tests'
	@echo 'build			- build the project --- NOT IMPLEMENTED!!'
	@echo 'force-release		- force a new release to be created in GitHub'
