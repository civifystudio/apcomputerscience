#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}")" )" && pwd )"

# Run the game using the system Python
python3 "$SCRIPT_DIR/main.py"