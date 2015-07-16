# -*-coding: utf-8 -*-


import re
import os
from datetime import datetime
from fabric.api import env, local, lcd


env.user = 'root'
env.password = 'Spcc12345'
env.sudo_user = 'root'
env.hosts = ['123.57.236.80']


db_user = 'root'
db_password = 'password'


_TAR_FILE = 'dist-weblog.tar.gz'


def build():
    print("aaaaaaaaaaaa")
    includes = ['static', 'templates', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -rf dist/%s' % _TAR_FILE)
    with lcd(os.path.join(os.path.abspath('.'), 'www')):
        cmd = ['tar', '--dereference', 'cvzf', '../dist/%s' % _TAR_FILE]
        cmd.extend(["--exclude='%s'" for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))
