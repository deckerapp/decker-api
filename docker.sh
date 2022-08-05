#!/bin/bash
sudo docker build -t twattle-api .
sudo docker stop twattle-api
sudo docker rm -v twattle-api
sudo docker run --name twattle-api -p 5000:5000 -d twattle-api
