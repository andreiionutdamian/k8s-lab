#!/bin/bash
source ../utils.sh

DEPLOYMENT_NAME="basic-test-py"
NAMESPACE="basic-ns11"
CHECK_INTERVAL=5

kubectl apply -f deploy.yaml

get_ready_replicas() {
    kubectl get deployment "$DEPLOYMENT_NAME" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}'
}

# Wait until all pods are ready
log_with_color "Waiting for pods of deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE' to become ready..." yellow
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
