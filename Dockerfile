FROM python:3.8.5-slim
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install python-dev --assume-yes
WORKDIR /authserver
ADD authserver authserver
ADD migrations migrations
ADD wsgi.py wsgi.py
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system && pipenv install --dev --system
ADD entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "/authserver/entrypoint.sh" ]
