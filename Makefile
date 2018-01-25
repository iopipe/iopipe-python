SHELL=/bin/bash

DOCKER_COMPOSE_YML?=docker-compose.yml

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8

test: test-python2 test-python3

test-python2: clean
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python2

test-python3: clean
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python3
