#!/bin/sh

# use the local django packages
export PYTHONPATH=${PWD}

PORT='8000'
CHECK_DARWIN=`uname -a | awk '/Darwin/ {split ($1,A,":"); print A[1]}'`
CHECK_LINUX=`uname  -a | awk '/Linux/  {split ($1,A,":"); print A[1]}'`

if [ ! -z $CHECK_DARWIN ]; then
	echo 'found Darwin ...'
	ADDR=`/sbin/ifconfig en0 | awk '/inet / {split ($2,A,":"); print A[1]}'`
fi

if [ ! -z $CHECK_LINUX ]; then
	echo 'found Linux ...'
	ADDR=`/sbin/ifconfig eth0 | awk '/inet Adr/ {split ($2,A,":"); print A[2]}'`

    if [ ! $ADDR ]; then
        echo "use eth1"
        ADDR=`/sbin/ifconfig eth1 | awk '/inet Adr/ {split ($2,A,":"); print A[2]}'`
    fi
fi

if [ $ADDR = "" ]; then
	echo 'can not detect your IP-Adress use localhost'
	ADDR=localhost
fi

echo '\nStarting django development server...\n'

export DJANGO_SETTINGS_MODULE=testproject.settings
(
	set -x
	django-admin.py runserver $ADDR":$PORT" $*
)

if [ $? != 0 ]; then
	echo "\ncommand failed\n"
	echo "Have you activate this environment?"
	echo "e.g.:"
	echo "source ~/pyrm_env/bin/activate"
fi 