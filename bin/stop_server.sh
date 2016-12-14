#!/bin/bash

if [ "$UID" -ne 0 ]; then
	echo "root privilege required, please use SUDO"
	exit
fi

SERVERROOT=/usr/local/

$SERVERROOT/nginx/sbin/nginx -s stop
kill -INT `cat /usr/local/php/var/run/php-fpm.pid`
