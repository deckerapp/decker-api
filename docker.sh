#!/bin/bash
sudo docker build -t derailed-api .
sudo docker stop derailed-api
sudo docker rm -v derailed-api
sudo docker run --name derailed-api -p 5000:5000 -d derailed-api
