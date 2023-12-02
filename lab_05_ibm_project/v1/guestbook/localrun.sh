#!/bin/bash

docker rmi local_run_lab1
docker build -t local_run_lab1 .
docker run --rm --name local_run_lab1_container -p 3000:3000 local_run_lab1
