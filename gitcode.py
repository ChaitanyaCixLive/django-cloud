__author__ = 'deepak'

from fabric.api import *
from fabric.contrib.files import upload_template
from fabfile import setupHost
import configproperties

def pullCode(hostAddress=configproperties.wolunteerHostIP, projectPath=configproperties.wolunteerProjectPath,
             key_file=configproperties.wolunteer_key_path):
    setupHost(hostAddress=hostAddress, key_file=key_file)
    with cd(projectPath):
        run('git pull')
    sudo('service apache2 reload')

def upload_private_key():
    setupHost(hostAddress=configproperties.wolunteerHostIP, key_file=configproperties.wolunteer_key_path)
    private_key_file = '/home/deepak/.ssh/id_rsa.rsa'
    dest = '/home/ubuntu/.ssh/id_rsa.rsa'
    upload_template(filename=private_key_file,
                    destination=dest,
                    use_jinja=False,
                    use_sudo=False,
                    context=None)
    run('chmod 400 ' + dest)



