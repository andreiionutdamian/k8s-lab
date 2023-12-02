#!/bin/bash

declare -A responses
declare -A times

url="http://localhost:30000/hello"
T=100  # Print message every T requests
NR_REQUESTS=5000
total_time=0
max_time=0
min_time=99999999


for i in $(seq $NR_REQUESTS); do
    if (( i % T == 0 )); then
        echo "Sending request number $i to $url"
    fi

    # Time the request and record the request time
    start_time=$(date +%s.%N)
    result=$(curl -sL "$url")
    end_time=$(date +%s.%N)
    elapsed=$(echo "$end_time - $start_time" | bc)
    total_time=$(echo "$total_time + $elapsed" | bc)

    # Update min and max time
    if [[ $i -eq 1 || $(echo "$elapsed < $min_time" | bc) -eq 1 ]]; then
        min_time=$elapsed
    fi
    if [[ $(echo "$elapsed > $max_time" | bc) -eq 1 ]]; then
        max_time=$elapsed
    fi

    # Record response
    if [[ -z ${responses["$result"]} ]]; then
        echo "New response: $result"
    fi
    ((responses["$result"]++))

    # Record time
    times["$i"]=$elapsed
done

# Calculate average time
average_time=$(echo "scale=4; $total_time / $NR_REQUESTS" | bc -l)

echo "Summary of responses:"
for response in "${!responses[@]}"; do
    echo "Hostname: $response -> ${responses[$response]} responses"
done

echo "Average time per request: $average_time seconds"
