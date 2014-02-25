#!/bin/bash

#eval `ssh-agent -s`
#ssh-add
cd /home/ubuntu
git clone {{ bitbucket_git_repo }}
cd {{ PROJECT_PATH }}
git pull origin master