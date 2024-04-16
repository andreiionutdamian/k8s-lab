#!/bin/bash

# Apply the Pod manifest
kubectl apply -f reader.yaml

# Wait for the Pod to be in the Running state
kubectl wait --for=condition=Ready pod/read-test --timeout=120s

# Follow the Pod logs
kubectl logs -f read-test

# Once you exit the log following (e.g., by pressing Ctrl+C), delete the Pod
kubectl delete -f reader.yaml
