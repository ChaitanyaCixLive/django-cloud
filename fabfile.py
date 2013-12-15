__author__ = 'deepak'

import os
import sys
from fabric.api import *
from fabric.contrib.files import upload_template


PROJECT_NAME = 'techvolunteer'
DOMAIN_NAME = 'completestack.net'
PROJECT_ROOT = '/home/ubuntu/techvolunteerproject'
ADMIN_EMAIL = 'deepakgarg.iitg@gmail.com'
PROJECT_APACHE_DIR = os.path.join(PROJECT_ROOT, 'apache2')
STATIC_URL = '/static/'

def setupHost(hostAddress='', user='', password='', key_file=''):
    sys.path.append(os.getcwd())
    try:
        import configproperties  #properties file containing default values
        if hostAddress is '':
            hostAddress=configproperties.hostIP
        if user is '':
            user=configproperties.userName
        if key_file is '':
            key_file=configproperties.key_path
    except Exception as ex:
        print('Default file named "configproperties" is not present')
    if password:
        env.password = password
    env.key_filename = key_file
    #TODO Check for key_file path
    env.host_string = hostAddress
    env.user = user

def start():
    setupHost()
    prepare_prod()

def usage():
    print('fab start \nor\nfab setup:host=<hostname>,user=<username>,key_file=<path-to-keyfile>')

def prepare_prod():
    install_baseline()
    install_py()
    create_directories()
    #basic_django()
    install_apache()
    configure_apache()
    configure_wsgi()
    activate_apache()
        
def install_baseline():
    sudo('apt-get update && apt-get -y upgrade')
    sudo('apt-get install -y fabric')
    sudo('apt-get install -y git-core build-essential curl vim')

def install_py():
    sudo(' apt-get install -y pep8 python python3 python-setuptools python-dev \
        python-django python-pip')
    sudo('pip install virtualenv')
    sudo('apt-get install -y python-mysqldb')
    #sudo('apt-get install sqlite3')

def create_directories():
    path = PROJECT_ROOT + '/{media,apache2}'
    run('mkdir -p ' + path )


def basic_django():
    with cd(PROJECT_ROOT):
        run('django-admin startproject ' + PROJECT_NAME)

def install_apache():
    sudo('apt-get install -y apache2 libapache2-mod-wsgi')

def configure_apache():
    #TODO fix this
    cwd = os.getcwd()
    temdir = os.path.join(cwd,'templates')
    dest = os.path.join('/etc/apache2/sites-available', DOMAIN_NAME)
    context = { 'SITE_NAME': DOMAIN_NAME,
                'ADMIN_EMAIL': ADMIN_EMAIL,
                'APACHE_DIR': PROJECT_APACHE_DIR,
                'PROJECT_ROOT': PROJECT_ROOT,
                'PROJECT_NAME': PROJECT_NAME,
                'STATIC_URL': STATIC_URL
        }
    upload_template(filename='apache_site.template',
                                     destination=dest,
                                     context=context,
                                     use_jinja=True,
                                     template_dir=temdir,
                                     use_sudo=True)

def configure_wsgi():
    cwd = os.getcwd()
    temdir = os.path.join(cwd,'templates')
    dest = os.path.join(PROJECT_APACHE_DIR, 'django.wsgi')
    context = { 'PROJECT_ROOT': PROJECT_ROOT,
                'PROJECT_NAME': PROJECT_NAME
        }
    upload_template(filename='django.wsgi.template',
                     destination=dest,
                     context=context,
                     use_jinja=True,
                     template_dir=temdir,
                     use_sudo=True)

def activate_apache():
    sudo('a2dissite default')
    sudo('a2ensite ' + DOMAIN_NAME)
    sudo('/etc/init.d/apache2 reload')


