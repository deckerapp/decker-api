#!/bin/bash
sudo docker build -t discorse-api .
sudo docker stop discorse-api
sudo docker rm -v discorse-api
sudo docker run --name discorse-api -p 5000:5000 -d discorse-api
