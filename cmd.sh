#!/bin/bash

gunicorn -b 0.0.0.0 -w 4 wsgi:app