#!/bin/bash
sudo docker build -t discend-api .
sudo docker stop discend-api
sudo docker rm -v discend-api
sudo docker run --name discend-api -p 5000:5000 -d discend-api
