SHELL=/bin/bash

DOCKER_COMPOSE_YML?=docker-compose.yml

test: test_python2 test_python3

test_python2:
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python2

test_python3:
	docker-compose -f ${DOCKER_COMPOSE_YML} build --no-cache python3
