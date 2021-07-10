.PHONY: all install lint test format

all: lint test

install:
	pip install -r requirements.dev.txt  -e .

compile:
	pip-compile setup.py && pip-compile requirements.dev.in

upgrade:
	pip-compile --upgrade setup.py && pip-compile --upgrade requirements.dev.in

lint:
	flake8 .
	pydocstyle comp
	isort --check-only .
	black --check .
	mypy comp


test:
	pytest tests

format:
	isort .
	black .
