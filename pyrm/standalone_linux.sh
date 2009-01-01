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
fi

if [ ! -z $ADDR ]; then
	echo 'Starting django development server...'
	python ./manage.py runserver ${ADDR}":$PORT" $*
else
	echo 'can not detect your IP-Adress'
fi
