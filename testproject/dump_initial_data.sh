#!/bin/sh

export DJANGO_SETTINGS_MODULE=testproject.settings

(
	set -x
	django-admin.py dumpdata pyrm.Status --indent=4
)
if [ $? != 0 ]; then
	echo "\ncommand failed\n"
	echo "Have you activate this environment?"
	echo "e.g.:"
	echo "source ~/pyrm_env/bin/activate"
fi 