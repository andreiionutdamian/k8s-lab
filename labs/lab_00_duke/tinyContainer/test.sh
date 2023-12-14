#!/usr/bin/env bash
# This script repeats a given string a specified number of times.
# Usage:
#   script.sh [--line] string [number]
# Arguments:
#   --line   - Optional. If present, output is printed in a single line.
#   string   - The string to repeat.
#   number   - Optional. The number of times to repeat the string (default: 1).
#   --help   - Displays this usage information.

# Function to print the usage information
usage() {
    echo "Usage: $0 [--line] string [number]"
    exit 1
}

# Function to print an error message and exit with a non-zero exit code
error() {
    echo "$0: $1" >&2
    exit 1
}

# Check for the --help parameter
if [ "$1" == "--help" ]; then
    usage
fi

# Initialize variables
line=false
number=1

# Check for the --line parameter
if [ "$1" == "--line" ]; then
    line=true
    shift
fi

# Check and set the string parameter
if [ -z "$1" ]; then
    usage # Call usage function if string is not provided
else
    string="$1"
    shift
fi

# Check and set the number parameter
if [ -n "$1" ]; then
    if ! [[ "$1" =~ ^[0-9]+$ ]]; then
        error "number must be a positive integer"
    fi
    number="$1"
fi

# Print the string the specified number of times
for (( i=0; i<number; i++ )); do
    if [ "$line" == true ]; then
        echo -n "$string " # Print on the same line with space separator
    else
        echo "$string" # Print on separate lines
    fi
done

# Print a newline if --line parameter was used
[ "$line" == true ] && echo
