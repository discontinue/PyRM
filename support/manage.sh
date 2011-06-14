#!/bin/sh

#
# This shell script is usefull, if you want to use django-admin with the
# local django packages and not with a normal installed django instance.
#

export DJANGO_SETTINGS_MODULE=pyrm_app.settings

python ../bin/django-admin.py $*