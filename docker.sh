#!/bin/bash
sudo docker build -t derailed-api .
sudo docker rm derailed-api
sudo docker run -d -p 5000:5000 derailed-api