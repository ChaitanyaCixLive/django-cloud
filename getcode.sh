#!/bin/bash

eval `ssh-agent -s`
ssh-add
cd /home/ubuntu
echo -e "Host bitbucket.org\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
git clone {{ bitbucket_git_repo }}
cd {{ PROJECT_PATH }}
git pull origin master