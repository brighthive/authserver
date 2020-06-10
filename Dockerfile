FROM python:3.7.4-slim
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
ADD cmd.sh cmd.sh
RUN chmod +x cmd.sh
ENTRYPOINT [ "/authserver/cmd.sh" ]
