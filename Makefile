.PHONY: all install lint test format

all: lint test

install:
	pip install -r requirements.dev.txt  -e .

upgrade:
	pip install --upgrade -r requirements.dev.txt  -e .

lint:
	ruff check .
	ruff format --check .
	mypy kotsu

test:
	pytest tests

format:
	ruff check --fix .
	ruff format .

package:
	python -m build


release: package
	python -m twine upload dist/*
