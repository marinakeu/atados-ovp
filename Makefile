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
