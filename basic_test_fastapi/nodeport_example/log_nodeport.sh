#!/bin/bash
NAMESPACE=basic-ns11
POD_NAME=$(kubectl get pods -n $NAMESPACE -o jsonpath="{.items[0].metadata.name}")
kubectl logs -n basic-ns11 $POD_NAME -f

