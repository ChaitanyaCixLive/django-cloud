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
    print('fab start:environ="<environment-name>"')

def prepare_prod():
    install_baseline()
    install_py()
    install_mysql()
    create_directories()
    #basic_django()
    install_apache()
    configure_apache()
    configure_wsgi()
    download_code()
    activate_apache()
        
def install_baseline():
    sudo('apt-get update && apt-get -y upgrade')
    sudo('apt-get install -y fabric')
    sudo('apt-get install -y git-core build-essential curl vim')

def install_py():
    sudo(' apt-get install -y pep8 python python3 python-setuptools python-dev \
        python-pip')
    # TODO - install specific version of django
    sudo(' apt-get install -y python-django')
    sudo('pip install virtualenv')
    sudo('apt-get install -y python-mysqldb')
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


def basic_django():
    with cd(PROJECT_PATH):
        run('django-admin startproject ' + PROJECT_NAME)

def install_apache():
    sudo('apt-get install -y apache2 libapache2-mod-wsgi')

def configure_apache():
    cwd = os.getcwd()
    temdir = os.path.join(cwd,'templates')
    dest = os.path.join('/etc/apache2/sites-available', DOMAIN_NAME)
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

def configure_wsgi():
    cwd = os.getcwd()
    temdir = os.path.join(cwd,'templates')
    dest = os.path.join(PROJECT_APACHE_DIR, 'django.wsgi')
    context = {
            'PROJECT_ROOT': PROJECT_PATH,
            'PROJECT_NAME': PROJECT_NAME
    }
    upload_template(filename='django.wsgi.template',
                     destination=dest,
                     use_jinja=True,
                     context=context,
                     template_dir=temdir,
                     use_sudo=True)

def download_code():
    ubuntu_home = '/home/ubuntu/'
    ssh_dir = ubuntu_home + '.ssh/'
    run('mkdir -p ' + ssh_dir )
    upload_template(filename='/home/deepak/.ssh/id_rsa',
                     destination=ssh_dir)
    upload_template(filename='/home/deepak/.ssh/config',
                    destination=ssh_dir)
    repo_name = PROJECT_PATH.split('/')[3]
    bitbucket_git_repo = 'ssh://git@bitbucket.org/deepakgarg/' + repo_name + '.git'
    context = {
       'PROJECT_PATH': PROJECT_PATH,
       'bitbucket_git_repo': bitbucket_git_repo
    }
    run('chmod 400 ' + ssh_dir + 'id_rsa')
    upload_template(filename='getcode.sh',
                 destination=ubuntu_home,
                 use_jinja=True,
                 context=context,
                 template_dir=os.getcwd(),
                 use_sudo=False)
    with cd(ubuntu_home):
        run('source getcode.sh')

    #bitbucket_http_repo = 'https://bitbucket.org/deepakgarg/' + repo_name
    #run('eval `ssh-agent -s`')
    ##run('ssh-add')
    #with cd('/home/ubuntu'):
    #    run('git clone ' + bitbucket_http_repo)
    #with cd(PROJECT_PATH):
    #    run('git remote remove origin')
    #    run('git remote add origin ' + bitbucket_git_repo)
    #    run('git pull origin master')

def activate_apache():
    sudo('a2dissite default')
    sudo('a2ensite ' + DOMAIN_NAME)
    sudo('/etc/init.d/apache2 reload')


