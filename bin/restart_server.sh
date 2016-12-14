#!/bin/bash

if [ "$UID" -ne 0 ]; then
	echo "root privilege required, please use SUDO"
	exit
fi

SERVERROOT=/usr/local/

$SERVERROOT/nginx/sbin/nginx -s reload
# 表示平滑重启
kill -USR2 `cat /usr/local/server/php/var/run/php-fpm.pid`
