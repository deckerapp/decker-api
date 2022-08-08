#!/bin/bash
sudo docker build -t elasic-api .
sudo docker stop elasic-api
sudo docker rm -v elasic-api
sudo docker run --name elasic-api -p 5000:5000 -d elasic-api
