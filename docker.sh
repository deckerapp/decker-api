#!/bin/bash
sudo docker build -t decker-api .
sudo docker stop decker-api
sudo docker rm -v decker-api
sudo docker run --name decker-api -p 5000:5000 -d decker-api
