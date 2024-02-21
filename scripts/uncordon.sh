#!/bin/bash

# Get all nodes with SchedulingDisabled status
nodes_with_scheduling_disabled=$(kubectl get nodes | grep SchedulingDisabled | awk '{print $1}')

# Check if the string is empty
if [[ -z "$nodes_with_scheduling_disabled" ]]; then
    echo "No nodes are currently marked as SchedulingDisabled."
else
    # If not empty, loop through each node and uncordon it
    for node in $nodes_with_scheduling_disabled; do
        echo "Uncordoning node: $node"
        kubectl uncordon "$node"
    done
    echo "Completed uncordoning nodes."
fi

