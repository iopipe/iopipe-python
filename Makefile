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

test: test-python2.7 test-python3.6 test-python3.7

test-python2.7: clean
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python2.7

test-python3.6: clean
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python3.6

test-python3.7: clean
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python3.7
