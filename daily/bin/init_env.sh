#!/bin/sh
if `test -d /var/data/log`
then
	echo '已经存在目录!'
else
	mkdir -p /var/data/log
	echo 'mkdir it ok!'
fi
