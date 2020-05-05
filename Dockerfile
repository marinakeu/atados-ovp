#	Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START docker]

# The Google App Engine python runtime is Debian Jessie with Python installed
# and various os-level packages to allow installation of popular Python
# libraries. The source is on github at:
# https://github.com/GoogleCloudPlatform/python-docker
FROM gcr.io/google_appengine/python

# Create a virtualenv for the application dependencies.
# # If you want to use Python 2, use the -p python2.7 flag.
RUN virtualenv -p python3.6 /env
ENV PATH /env/bin:$PATH

ENV PYTHONUNBUFFERED 1
ADD requirements.txt /app/requirements.txt
ADD api/django-ovp/requirements /app/api/django-ovp/requirements
RUN /env/bin/pip install --upgrade pip && /env/bin/pip install -r /app/requirements.txt
RUN pip install gunicorn

RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
  && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
  && locale-gen

ADD . /app

ENV DJANGO_ENV=production
CMD cd /app/api && gunicorn -b :$PORT server.wsgi:application -w 5 --timeout 300 --limit-request-line 16382
# [END docker]
