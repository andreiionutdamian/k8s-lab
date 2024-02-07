#!/bin/bash

source ../utils.sh

APP_NAME="basic-test-py"
NAMESPACE="basic-ns11"
kubectl delete -f deploy_nodeport.yaml

# Wait for the pods to be deleted
while true; do 
  OUTPUT=$(kubectl get pods -l run=$APP_NAME -n $NAMESPACE 2>&1)
  echo "$OUTPUT"
  if [[ "$OUTPUT" == *"No resources found"* ]]; then
    log_with_color "All pods terminated." green
    break
  fi
  sleep 5
done
