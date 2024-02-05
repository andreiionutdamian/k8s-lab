#!/bin/bash
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

# SSH Key Location
SSH_KEY="~/.ssh/mihai.pem"
# User on the remote nodes
USER="neural"

# Check for debug/test mode
if [[ "$1" == "debug" || "$1" == "test" || "$1" == "test-only" ]]; then
    DEBUG_MODE="true"
    log_with_color "Running in debug/test mode. No actions will be performed." yellow
else
    DEBUG_MODE="false"
fi

# Function to get all nodes with their roles
get_nodes() {
    # Get all nodes, their roles, and external IPs
    readarray -t NODES < <(kubectl get nodes -o=jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}')

    # Initialize arrays
    WORKER_NODES=()
    CONTROL_PLANE_NODES=()

    # Separate worker and control plane nodes based on role
    for line in "${NODES[@]}"; do
        node_name=$(echo $line | awk '{ print $1}')
        node_ip=$(echo $line | awk '{ print $2}')
        log_with_color "Getting role for node: $node_name, IP: $node_ip"
        if kubectl get node $node_name -o jsonpath='{.metadata.labels}' | grep 'node-role\.kubernetes\.io/master\|node-role\.kubernetes\.io/control-plane' &> /dev/null; then
            CONTROL_PLANE_NODES+=("$node_name@$node_ip")
            log_with_color "Found control plane node: $node_name@$node_ip"
        else
            WORKER_NODES+=("$node_name@$node_ip")
            log_with_color "Found worker node: $node_name@$node_ip"
        fi
    done
}

# Function to drain nodes
drain_node() {
    if [[ "$DEBUG_MODE" == "true" ]]; then
        log_with_color "[DEBUG] Would drain node $1"
    else
        log_with_color "Draining node $1"
        kubectl drain $1 --ignore-daemonsets --delete-emptydir-data --force
    fi
}

# Function to shutdown nodes
shutdown_node() {
    local node_info=$1 # Contains node_name@node_ip
    local node_ip=$(echo "$node_info" | awk -F'@' '{print $2}')
    local node_name=$(echo "$node_info" | awk -F'@' '{print $1}')
    if [[ "$DEBUG_MODE" == "true" ]]; then
        log_with_color "[DEBUG] Would shutdown node $node_name via ssh -i $SSH_KEY $USER@$node_ip"
    else
        log_with_color "Shutting down node $node_name via ssh $USER@$node_ip"
        ssh -i "$SSH_KEY" "$USER@$node_ip" "sudo shutdown now"
    fi
}

# Execute node operations
run_operations() {
    log_with_color "Workers to be drained and shutdown:"
    for node in "${WORKER_NODES[@]}"; do
        log_with_color "  - $node"
    done

    log_with_color "Masters to be drained and shutdown:"
    for node in "${CONTROL_PLANE_NODES[@]}"; do
        log_with_color "  - $node"
    done

    # Drain and shutdown worker nodes
    log_with_color "Draining and shutting down worker nodes" yellow
    for node_info in "${WORKER_NODES[@]}"; do
        local node_name=$(echo "$node_info" | awk -F'@' '{print $1}')
        drain_node $node_name
        shutdown_node $node_info
    done

    # Optionally wait a bit for all worker nodes to be completely down
    [[ "$DEBUG_MODE" == "false" ]] && log_with_color "Sleeping 60s or all worker nodes to be completely down" yellow && sleep 60

    # Drain and shutdown control plane nodes
    log_with_color "Draining and shutting down control plane nodes" yellow
    for node_info in "${CONTROL_PLANE_NODES[@]}"; do
        local node_name=$(echo "$node_info" | awk -F'@' '{print $1}')
        drain_node $node_name
        shutdown_node $node_info
    done
}

# Main
get_nodes
run_operations

[[ "$DEBUG_MODE" == "false" ]] && echo "Cluster shutdown sequence completed." || echo "Debug/test mode complete. No real actions were taken."
