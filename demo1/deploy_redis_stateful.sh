#!/bin/bash

./stop.sh
docker rmi guestbook:v1
docker build -t guestbook:v1 .
kubectl apply -f ./manifest/redis-stateful/
