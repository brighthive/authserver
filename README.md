# Brighthive Authorization and Authentication Server [![Documentation Status](https://readthedocs.org/projects/brighthive-authserver/badge/?version=latest)](https://brighthive-authserver.readthedocs.io/en/latest/?badge=latest)

An OAuth 2.0 server with added services for providing fine-grain access control to Data Trust assets.

# Getting Started

### Run the App Locally

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

**4. (second terminal)Run the Flask app!**

```
pipenv run ./entrypoint.sh
```

Hurrah! Check the app status here: `http://0.0.0.0:10001/health`

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
