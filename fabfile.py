import json

__author__ = 'deepak'

import os
import sys
from fabric.api import *
from fabric.contrib.files import upload_template


PROJECT_NAME = ''
DOMAIN_NAME = ''
PROJECT_PATH = ''
ADMIN_EMAIL = 'deepakgarg.iitg@gmail.com'
PROJECT_APACHE_DIR = '/home/ubuntu/apachewsgi'
STATIC_URL = '/static/'
MYSQL_ROOT_PASSWORD = ''
GIT_SSH_FILE = ''
STATIC_DIR = ''

def setupHost(environ):
    global PROJECT_PATH, PROJECT_NAME, DOMAIN_NAME, MYSQL_ROOT_PASSWORD, GIT_SSH_FILE, STATIC_DIR
    sys.path.append(os.getcwd())
    with open('config.json') as data:
        json_data = json.load(data)
        env_dic = json_data[environ]
    env.key_filename = env_dic["host_key"]
    env.host_string = env_dic["ip"]
    env.user = env_dic["username"]
    PROJECT_PATH = env_dic["project_path"]
    PROJECT_NAME = env_dic["project_name"]
    DOMAIN_NAME = env_dic["domain_name"]
    MYSQL_ROOT_PASSWORD = env_dic["mysql_password"]
    GIT_SSH_FILE = env_dic["git_ssh_file"]
    STATIC_DIR = env_dic["static_dir"]

def deploy(environ='personalweb'):
    setupHost(environ)
    prepare_prod()

def usage():
    print('fab deploy:environ="<environment-name>"')

def prepare_prod():
    install_baseline()
    install_py()
    install_mysql()
    create_directories()
    install_apache()
    configure_apache()
    download_code()
    activate_apache()
        
def install_baseline():
    sudo('apt-get update && apt-get -y upgrade')
    sudo('apt-get install -y fabric')
    sudo('apt-get install -y git-core build-essential curl vim')

def install_py():
    sudo(' apt-get install -y pep8 python python-setuptools python-dev \
        python-pip')
    sudo('apt-get install -y python-mysqldb')
    # TODO - install specific version of django
    sudo(' apt-get install -y python-django')
    # sudo('pip install virtualenv')
    #sudo('apt-get install sqlite3')

def install_mysql():
    debconf1 = "debconf-set-selections <<< 'mysql-server mysql-server/root_password password %s' " % (MYSQL_ROOT_PASSWORD,)
    debconf2 = "debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password %s' " % (MYSQL_ROOT_PASSWORD,)
    sudo(debconf1)
    sudo( debconf2 )
    sudo("apt-get -y install mysql-server ")
    sudo("apt-get -y install libmysqlclient-dev")

def create_directories():
    run('mkdir -p ' + PROJECT_APACHE_DIR )

def install_apache():
    sudo('apt-get install -y apache2 libapache2-mod-wsgi')

def configure_apache():
    cwd = os.getcwd()
    temdir = os.path.join(cwd,'templates')
    apache_file_name = DOMAIN_NAME.split('.')[0] + '.conf'
    dest = os.path.join('/etc/apache2/sites-available', apache_file_name)
    context = { 'SITE_NAME': DOMAIN_NAME,
                'ADMIN_EMAIL': ADMIN_EMAIL,
                'APACHE_DIR': PROJECT_APACHE_DIR,
                'PROJECT_ROOT': PROJECT_PATH,
                'PROJECT_NAME': PROJECT_NAME,
                'STATIC_URL': STATIC_URL,
                'STATIC_DIR' : STATIC_DIR
        }
    upload_template(filename='apache_site.template',
                                     destination=dest,
                                     context=context,
                                     use_jinja=True,
                                     template_dir=temdir,
                                     use_sudo=True)


def download_code():
    ubuntu_home = '/home/ubuntu/'
    ssh_dir = ubuntu_home + '.ssh/'
    temdir = os.path.join(os.getcwd(),'templates')
    run('mkdir -p ' + ssh_dir )

    upload_template(filename='/home/deepak/.ssh/id_rsa',
                     destination=ssh_dir)
    upload_template(filename=os.path.join(temdir, 'config'),
                    destination=ssh_dir)
    repo_name = PROJECT_PATH.split('/')[3]
    bitbucket_git_repo = 'ssh://git@bitbucket.org/deepakgarg/' + repo_name + '.git'
    run('chmod 400 ' + ssh_dir + 'id_rsa')
    with cd(ubuntu_home):
        run('git clone ' + bitbucket_git_repo)
    with cd( PROJECT_PATH ):
        run('git pull origin master')
        sudo('pip install -r pip.txt') #todo don't do this step for personalweb environment
        #run('python manage.py syncdb') #todo - syncdb


def activate_apache():
    sudo('a2dissite 000-default.conf')
    sudo('a2ensite ' + DOMAIN_NAME.split('.')[0])
    sudo('sudo service apache2 reload')
    #for anniecreative do:
#    cd /var/www/media
#chgrp -R www-data geekingreen/
#chmod -R g+w geekingreen/


