#!/bin/bash

if [ "$APP_ENV" == "DEVELOPMENT" ] || [ -z "$APP_ENV" ]; then
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app --reload
else
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
    gunicorn -b 0.0.0.0 -w $WORKERS wsgi:app
fi