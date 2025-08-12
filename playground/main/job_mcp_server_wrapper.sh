#!/bin/bash

# MCP Server Wrapper Script
# This ensures the virtual environment is activated before running the MCP server

echo "=== MCP Server Wrapper Starting ===" >&2

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR" >&2

# Virtual environment path
VENV_PATH="/Users/brian.liu/Desktop/Coding/anthropic-local-test/.venv"
echo "Virtual environment path: $VENV_PATH" >&2

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH" >&2
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..." >&2
source "$VENV_PATH/bin/activate"

# Verify activation
echo "Python executable: $(which python3)" >&2
echo "Python version: $(python3 --version)" >&2

# Change to the script directory
cd "$SCRIPT_DIR"
echo "Changed to directory: $(pwd)" >&2

# Run the MCP server
echo "Starting MCP server..." >&2
exec python3 job_mcp_server.py 