#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
@author: fengkai
@contact: kaifeng@whu.edu.cn
@file: INSTALL.py
@date: 16-12-11
"""

import os
import sys
import platform
from multiprocessing import cpu_count


def sysexit(s, status):
    print(s)
    sys.exit(status)


try:
    from fabric.api import *
except ImportError:
    sysexit('You must install fabric. Trying input <pip2.7 install fabric>.', 1)



# 获取当前工作目录
cdir = os.getcwd()
# 系统cpu个数
cpus = cpu_count()


def check():
    print('**********Checking for dependency**********')
    if 'centos' not in platform.uname()[3].lower():
        # sysexit('This program must be run in CentOS. Aborting.', 1)
        pass

    if os.geteuid() != 0:
        sysexit('This program must be run as ROOT. Aborting.', 1)

    dependency = ('gcc', 'gcc-c++', 'autoconf', 'automake', 'zlib', 'zlib-devel', 'openssl',
                  'openssl-devel', 'pcre', 'pcre-devel', 'libxml2-devel', 'libcurl-devel')
    for d in dependency:
        local('yum install -y %s > /dev/null' % d)


def mysql():
    print('\r\n**********Installing Mysql**********')
    local('yum install -y mysql-server mysql > /dev/null && service mysqld start && mysql_secure_installation')


def nginx():
    print('\r\n**********Installing Nginx**********')

    with lcd(cdir):
        local('tar -zxf nginx-1.10.1.tar.gz')

    with lcd(os.path.join(cdir, 'nginx-1.10.1')):
        local('./configure --prefix=/usr/local/nginx_1.10.1 --user=www --group=www --add-module='
              + os.path.join(cdir, 'nginx-rtmp-module') +
              ' > /dev/null && make -j ' + str(cpus) + ' > /dev/null && make install > /dev/null')

    with lcd('/usr/local/'):
        local('ln -s nginx_1.10.1 nginx')

    with lcd('/usr/local/nginx/conf/'):
        local('cp ' + os.path.join(cdir, 'nginx.conf') + ' nginx.conf')


def php():
    print('\r\n**********Installing PHP, Waiting for minutes**********')

    with lcd(cdir):
        local('tar -jxf php-7.0.8.tar.bz2')

    with lcd(os.path.join(cdir, 'php-7.0.8')):
        local('./configure --prefix=/usr/local/php-7.0.8 --with-fpm-user=www --with-fpm-group=www --enable-fpm --with-zlib --with-curl > /dev/null\
            && make -j ' + str(cpus) + ' > /dev/null && make install > /dev/null ')

    with lcd('/usr/local/'):
        local('ln -s php-7.0.8 php')

    with lcd('/usr/local/php/etc/'):
        local('cp php-fpm.conf.default php-fpm.conf')
        local('cp ' + os.path.join(cdir, 'php-7.0.8/php.ini-production') + ' php.ini')

    with lcd('/usr/local/php/etc/php-fpm.d'):
        local('cp www.conf.default www.conf')

    # with lcd('/usr/local/php/etc/'):
    #     f = open('php-fpm.conf', 'w+')
    #     data = f.read()
    #     import re
    #     re.sub(r";pid", 'pid', data)
    #     f.write(data)
    #     f.close()


def finish():
    print('\r\n**********Configuring and Cleaning up**********')

    # 檢測www用戶是否存在,不存在則創建
    with lcd(cdir):
        local("cat /etc/passwd | awk -F: '{print $1}' | grep ^www$ > www")
        if not os.path.getsize('www'):
            local('useradd -M -s /sbin/nologin www')
        local('rm www')

    # 创建web根目录
    if not os.path.exists('/data/web/'):
        local('mkdir -p /data/web/')

    with lcd(cdir):
        local('tar -zxf www.tar.gz -C /data/web/')

    local('chown -R www:www /data')


def main():
    print("""This program will install:
    1) mysql+nginx+php (Default)
    2) nginx+php
    3) nginx
    4) php""")
    s = '1'
    while True:
        s = raw_input('Please choice (Default 1): ')
        if not s:
            s = '1'
        if s in ('1', '2', '3', '4'):
            break
    check()
    s = int(s)
    if not s or s == 1:
        nginx()
        php()
        mysql()
    elif s == 2:
        nginx()
        php()
    elif s == 3:
        nginx()
    elif s == 4:
        php()

    finish()

    print('\r\n********** Installation Complete. More info please read *README*. **********\r\n')


if __name__ == '__main__':
    main()
