# TODO: Instalar deps do SO, ex: deps para PIL
clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements.txt

migrations:
	@python api/manage.py makemigrations

migrate:
	@python api/manage.py migrate

run:
	@python api/manage.py runserver 0.0.0.0:8000

# Start docker containers for the api and the database
run-docker:
	@docker-compose up

# Build docker images
docker:
	@docker-compose build api

# Connect to the api's running container with bash
docker-shell:
	@docker exec -it ovp-api bash

# Connect to the database's running container with bash
docker-db-shell:
	@docker exec -it ovp-db bash

# docker-compose entrypoint for the api's container to run migrations and then run the server
docker-entrypoint:
	@python api/manage.py migrate
	@python api/manage.py runserver 0.0.0.0:8000

test:
	@python api/manage.py test

setup: deps migrate run

shell:
	@python api/manage.py shell

collectstatic:
	@python api/manage.py collectstatic --noinput

sshadd:
	@eval `ssh-agent`
	@sudo ssh-add -K ~/.ssh/id_rsa

help:
	grep '^[^#[:space:]].*:' Makefile | awk -F ":" '{print $$1}'
