#!/bin/bash

kubectl delete \
  service/guestbook \
  deployment/guestbook \
  hpa/guestbook \
  service/redis-master \
  service/redis-slave \
  deployment/redis-master \
  deployment/redis-slave  \
  statefulset/redis-master \
  statefulset/redis-slave

kubectl delete pvc --all
kubectl delete pv --all # can delete as they are recreated on paths

