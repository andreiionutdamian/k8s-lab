#!/bin/bash
NAMESPACE=basic-postgres
POD_NAME=$(kubectl get pods -n $NAMESPACE -o jsonpath="{.items[0].metadata.name}")
kubectl logs -n $NAMESPACE $POD_NAME -f

