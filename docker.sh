#!/bin/bash
sudo docker build -t couchub-api .
sudo docker stop couchub-api
sudo docker rm -v couchub-api
sudo docker run --name couchub-api -p 5000:5000 -d couchub-api
