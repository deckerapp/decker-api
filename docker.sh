#!/bin/bash
docker build -t derailed-api .
docker rm derailed-api
docker run -d -p 5000:5000 derailed-api