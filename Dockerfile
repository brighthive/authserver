FROM python:3.7.4-slim
WORKDIR /authserver
ADD authserver authserver
ADD migrations migrations
ADD wsgi.py wsgi.py
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pip install pipenv && pipenv install --system && pipenv install --dev --system
ADD cmd.sh cmd.sh
RUN chmod +x cmd.sh
ENTRYPOINT [ "/authserver/cmd.sh" ]
