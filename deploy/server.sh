#!/bin/bash

cd ..
PRJ=`pwd | rev | cut -d "/" -f2 | rev`
gunicorn api.server.wsgi:application -w 5 --timeout 300 --limit-request-line 16382 --bind unix:/tmp/api.$PRJ.socket
#celery -A atados worker --app=atados.celery_app:app --loglevel=info
