#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /home/ubuntu/flask-api
git pull

source ~/.profile
echo "$DOCKERHUB_PASS" | sudo docker login --username $DOCKERHUB_USER --password-stdin
sudo docker stop helloworld
sudo docker rm helloworld
sudo docker rmi idkaryadi/helloworld
sudo docker run -d --name helloworld -p 5000:5000 idkaryadi/helloworld:latest

