#!/bin/bash

source ../utils.sh

APP_NAME="basic-test-py"
NAMESPACE="basic-clusters"
kubectl delete -f deploy.yaml

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
