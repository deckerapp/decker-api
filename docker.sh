#!/bin/bash
sudo docker build -t clack-api .
sudo docker stop clack-api
sudo docker rm -v clack-api
sudo docker run --name clack-api -p 5000:5000 -d clack-api
