FROM python:3.6
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
RUN pip install psycopg2-binary
ADD . /www/
