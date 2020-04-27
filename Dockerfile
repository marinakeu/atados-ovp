FROM python:3.6

RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen

ENV PYTHONUNBUFFERED 1
RUN mkdir /www
WORKDIR /www
# Installing OS Dependencies
RUN apt-get update && apt-get upgrade -y && \
  apt-get install -y libsqlite3-dev && \
  apt-get install git
RUN pip install -U pip setuptools
COPY requirements.txt /www/requirements.txt
COPY api/django-ovp/requirements /www/api/django-ovp/requirements
RUN pip install -r /www/requirements.txt
RUN pip install psycopg2-binary pudb Werkzeug
ADD . /www/
