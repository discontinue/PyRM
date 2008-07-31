#!/bin/sh

# use the local django packages
export PYTHONPATH=${PWD}

addr=`/sbin/ifconfig eth0 | awk '/inet Adr/ {split ($2,A,":"); print A[2]":8000"}'`

echo 'Starting django development server...'
python ./manage.py runserver ${addr} $*

