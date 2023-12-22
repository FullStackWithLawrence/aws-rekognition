SHELL := /bin/bash
ifeq ($(OS),Windows_NT)
    PYTHON = python.exe
    ACTIVATE_VENV = venv\Scripts\activate
else
    PYTHON = python3.11
    ACTIVATE_VENV = source venv/bin/activate
endif
PIP = $(PYTHON) -m pip

.PHONY: env analyze init pre-commit requirements lint clean test build force-release publish-test publish-prod help

# Default target executed when no arguments are given to make.
all: help

env:
	ifneq ("$(wildcard .env)","")
		include .env
	else
		$(shell echo -e "AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT=10" >> .env)
		$(shell echo -e "AWS_REKOGNITION_FACE_DETECT_THRESHOLD=10" >> .env)
		$(shell echo -e "AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES=DEFAULT" >> .env)
		$(shell echo -e "AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER=AUTO" >> .env)
		$(shell echo -e "AWS_DYNAMODB_TABLE_ID=rekognition" >> .env)
		$(shell echo -e "AWS_REGION=us-east-1" >> .env)
		$(shell echo -e "AWS_REKOGNITION_COLLECTION_ID=rekognition-collection" >> .env)
		$(shell echo -e "DEBUG_MODE=False" >> .env)
	endif

analyze:
	cloc . --exclude-ext=svg,zip --vcs=git

# -------------------------------------------------------------------------
# Initialize. create virtual environment and install requirements
# -------------------------------------------------------------------------
init:
	make clean && \
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	$(PIP) install --upgrade pip && \
	make requirements

# -------------------------------------------------------------------------
# Install requirements: Python, npm and pre-commit
# -------------------------------------------------------------------------
requirements:
	rm -rf .tox && \
	$(PIP) install --upgrade pip wheel && \
	$(PIP) install -r requirements.txt && \
	npm install && \
	pre-commit install && \
	pre-commit autoupdate && \
	pre-commit run --all-files

# -------------------------------------------------------------------------
# Run black and pre-commit hooks.
# includes prettier, isort, flake8, pylint, etc.
# -------------------------------------------------------------------------
lint:
	pre-commit run --all-files && \
	pylint ./terraform/python/rekognition_api && \
	flake8 . && \
	isort . && \
	black ./terraform/python/rekognition_api && \
	terraform fmt -recursive

# -------------------------------------------------------------------------
# Destroy all build artifacts and Python temporary files
# -------------------------------------------------------------------------
clean:
	rm -rf ./terraform/.terraform venv .pytest_cache __pycache__ .pytest_cache node_modules && \
	rm -rf build dist aws-rekogition.egg-info && \
	find ./terraform/python/ -name __pycache__ -type d -exec rm -rf {} +

# -------------------------------------------------------------------------
# Run Python unit tests
# -------------------------------------------------------------------------
test:
	python -m unittest discover -s terraform/python/rekognition_api/tests/

# -------------------------------------------------------------------------
# Force a new semantic release to be created in GitHub
# -------------------------------------------------------------------------
force-release:
	git commit -m "fix: force a new release" --allow-empty && git push

update:
	npm install -g npm && \
	npm install -g npm-check-updates && \
	ncu --upgrade --packageFile ./package.json && \
	npm update -g && \
	make init

build:
	cd terraform && \
	terraform init

# -------------------------------------------------------------------------
# Generate help menu
# -------------------------------------------------------------------------
help:
	@echo '===================================================================='
	@echo 'init			- build virtual environment and install requirements'
	@echo 'analyze			- runs cloc report'
	@echo 'requirements		- install Python, npm and pre-commit requirements'
	@echo 'lint			- run black and pre-commit hooks'
	@echo 'clean			- destroy all build artifacts'
	@echo 'test			- run Python unit tests'
	@echo 'build			- build the project --- NOT IMPLEMENTED!!'
	@echo 'force-release		- force a new release to be created in GitHub'
