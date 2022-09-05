.PHONY: all install lint test format

all: lint test

install:
	pip install -r requirements.dev.txt  -e .

upgrade:
	pip install --upgrade -r requirements.dev.txt  -e .

lint:
	flake8 .
	pydocstyle kotsu
	isort --check-only .
	black --check .
	mypy kotsu

test:
	pytest tests

format:
	isort .
	black .

package:
	python setup.py sdist
	python setup.py bdist_wheel


release: package
	twine upload dist/*
