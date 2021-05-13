#!/bin/bash

MAX_RETRIES=5
WORKERS=4
RETRIES=0
until flask db upgrade; do
    RETRIES=`expr $RETRIES + 1`
    if [[ "$RETRIES" -eq "$MAX_RETRIES" ]]; then
        echo "Retry Limit Exceeded. Aborting..."
        exit 1
    fi
    sleep 2
done

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    export AUTHLIB_INSECURE_TRANSPORT=1
    gunicorn -w 4 -b 0.0.0.0:10001 wsgi:app --reload --worker-class gevent --timeout 600
else
    gunicorn -b 0.0.0.0 -w $WORKERS wsgi:app --worker-class gevent
fi