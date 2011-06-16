#!/bin/sh

#
# This shell script is usefull, if you want to use django-admin with the
# local django packages and not with a normal installed django instance.
#

export DJANGO_SETTINGS_MODULE=testproject.settings

(
	set -x
	django-admin.py $*
)
if [ $? != 0 ]; then
	echo "\ncommand failed\n"
	echo "Have you activate this environment?"
	echo "e.g.:"
	echo "source ~/pyrm_env/bin/activate"
fi 