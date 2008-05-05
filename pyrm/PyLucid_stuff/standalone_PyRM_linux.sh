#!/bin/sh

#export DJANGO_SETTINGS_MODULE=PyRM_settings

# use the local django packages
export PYTHONPATH=${PWD}

while :
do
    echo 'Starting django development server...'

    python ./django/bin/django-admin.py runserver --settings=PyRM_settings $*

    ping localhost -n 1>NUL

    echo ''
    echo 'restart des Servers mit ENTER...'
    read
done

echo 'ENTER zum Beenden.'
read
