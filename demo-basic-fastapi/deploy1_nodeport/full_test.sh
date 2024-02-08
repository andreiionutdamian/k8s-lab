#!/bin/bash
source ../utils.sh

MACHINE_IP="192.168.1.55"

# manifest filename
MANIFEST_FILENAME="deploy.yaml"

# Name of the deployment
DEPLOYMENT_NAME="basic-test-py"

# Namespace where the deployment is located
# Update this if your deployment is not in the default namespace
NAMESPACE="basic-ns11"

# Interval in seconds between checks
CHECK_INTERVAL=5

COUNT=5


kubectl apply -f $MANIFEST_FILENAME

# Function to get the deployment's ready replicas
get_ready_replicas() {
    kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}'
}

# Wait until all pods are ready
log_with_color "Waiting for pods of deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE' to become ready..." blue
while true; do
    READY_REPLICAS=$(get_ready_replicas)
    
    # Check if the ready replicas count is non-empty and greater than 0
    if [[ "$READY_REPLICAS" != "" && "$READY_REPLICAS" -gt 0 ]]; then
        TOTAL_REPLICAS=$(kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
        
        if [[ "$READY_REPLICAS" == "$TOTAL_REPLICAS" ]]; then
            log_with_color "All $READY_REPLICAS pods are ready." green
            break
        else
            log_with_color "$READY_REPLICAS out of $TOTAL_REPLICAS pods are ready. Waiting..." yellow
        fi
    else
        log_with_color "No pods are ready yet. Waiting..." red
    fi
    
    sleep "$CHECK_INTERVAL"
done

for i in $(seq 1 $COUNT); do
  curl -L "http://$MACHINE_IP:30050"
  echo " "
done

for i in $(seq 1 $COUNT); do
  curl -L "http://$MACHINE_IP:30050/some_route"
  echo " "
done

log_with_color "Test completed." green
log_with_color "Deleting deployment $MANIFEST_FILENAME..." blue
kubectl delete -f $MANIFEST_FILENAME
log_with_color "Deployment deleted." green
