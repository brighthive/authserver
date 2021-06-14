FROM python:3.8.5-slim
WORKDIR /authserver
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install python-dev --assume-yes
ADD migrations migrations
ADD wsgi.py wsgi.py
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system && pipenv install --dev --system
ADD entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh
ADD authserver authserver
ENTRYPOINT [ "/authserver/entrypoint.sh" ]
