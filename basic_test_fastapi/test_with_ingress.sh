#!/bin/bash

# manifest filename
MANIFEST_FILENAME="deploy_with_ingress.yaml"

# Name of the deployment
DEPLOYMENT_NAME="basic-test-py"

# Namespace where the deployment is located
# Update this if your deployment is not in the default namespace
NAMESPACE="basic-ns12"

# Interval in seconds between checks
CHECK_INTERVAL=5


log_with_color() {
    local text="$1"
    local color="$2"
    local color_code=""

    case $color in
        red)
            color_code="0;31" # Red
            ;;
        green)
            color_code="0;32" # Green
            ;;
        blue)
            color_code="0;34" # Blue
            ;;
        yellow)
            color_code="0;33" # Yellow
            ;;
        light)
            color_code="1;37" # Light (White)
            ;;
        gray)
            color_code="2;37" # Gray (White)
            ;;
        *)
            color_code="0" # Default color
            ;;
    esac

    echo -e "\e[${color_code}m${text}\e[0m"
}

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
  curl -L http://localhost:30050
done

log_with_color "Test completed." green
log_with_color "Deleting deployment $MANIFEST_FILENAME..." blue
kubectl delete -f $MANIFEST_FILENAME
log_with_color "Deployment deleted." green
