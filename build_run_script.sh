#!/bin/bash

docker build -t devops-course:latest .
docker run -it -p 5000:5000 devops-course:latest