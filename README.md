# Brighthive Authorization and Authentication Server [![Documentation Status](https://readthedocs.org/projects/brighthive-authserver/badge/?version=latest)](https://brighthive-authserver.readthedocs.io/en/latest/?badge=latest)

An OAuth 2.0 server with added services for providing fine-grain access control to Data Trust assets.

# Getting Started

## Run the App Locally

Authserver is a Flask app with a REST interface supported by a Postgres database. Follow these steps to run the app locally:

**1. (first terminal) Stand up the Postgres database with `docker-compose`.**

```
docker-compose -f docker-compose-devel.yml up postgres
```

**2. (second terminal) Configure the app.** Authserver configures itself with environment variables. Copy `.env.development` to get started with local development:

```
cp .env.development .env
```

**3. (second terminal) Install dependencies.**

```
pipenv install --dev
```

**4. (second terminal) Run the Flask app!**

```
# Run migrations
pipenv run flask db upgrade

# Optionally, run the sql file 'run-locally.sql' to allow locally logging in to facet
docker exec -it postgres-authserver psql -U brighthive_admin -d authserver

# Run the app
pipenv run gunicorn -w 4 -b 0.0.0.0:10001 wsgi:app --reload --worker-class gevent --timeout 600

# Conversely, you can run the app with flask
pipenv run flask run -p 10001
```

Hurrah! Check the app status here: `http://0.0.0.0:10001/health`

## Run tests

```
APP_ENV=test pipenv run pytest
```

## Machine to machine admin credentials

To give a machine to machine credentials admin rights, you must manually enable it. There are no endpoints. This was done because super admin credentials are dangerous. In the `oauth2_clients` table you will find a `grant_super_admin` column. Set this to `True`.

## How to generate a JWT key pair

```
ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
# Don't add passphrase
openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
cat jwtRS256.key
cat jwtRS256.key.pub
```

- Taken from https://gist.github.com/ygotthilf/baa58da5c3dd1f69fae9

---

### Visual Studio Code Configuration

Most Brighthive engineers use [Visual Studio Code](https://code.visualstudio.com/) as their primary IDE. Below is a basic configuration that will work for this application.

```json
{
  "python.pythonPath": "/path/to/python",
  "python.linting.pycodestyleEnabled": true,
  "python.linting.pycodestylePath": "pycodestyle",
  "python.formatting.autopep8Path": "autopep8",
  "python.linting.pycodestyleArgs": ["--ignore=E501,E0239"],
  "python.formatting.autopep8Args": ["--ignore=E501,E0239"],
  "python.linting.pylintEnabled": false,
  "python.linting.enabled": true,
  "python.analysis.disabled": ["inherit-non-class"]
}
```
