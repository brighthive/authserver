# BrightHive Authorization and Authentication Server [![Documentation Status](https://readthedocs.org/projects/brighthive-authserver/badge/?version=latest)](https://brighthive-authserver.readthedocs.io/en/latest/?badge=latest)

An OAuth 2.0 server with added services for providing fine-grain access control to Data Trust assets.

## For Developers

### Visual Studio Code Configuration

Most BrightHive engineers use [Visual Studio Code](https://code.visualstudio.com/) as their primary IDE. Below is a basic configuration that will work for this application.

```json
{
    "python.pythonPath": "/path/to/python",
    "python.linting.pep8Enabled": true,
    "python.linting.pep8Path": "pycodestyle",
    "python.formatting.autopep8Path": "autopep8",
    "python.linting.pep8Args": [
        "--ignore=E501,E0239"
    ],
    "python.formatting.autopep8Args": [
        "--ignore=E501,E0239"
    ],
    "python.linting.pylintEnabled": false,
    "python.linting.enabled": true,
    "python.analysis.disabled": ["inherit-non-class"]
}
```
