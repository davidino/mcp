#!/bin/bash
# Install dependencies and run the MCP server from the local directory
cd "$(dirname "$0")"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q boto3 loguru mcp pydantic

# Run the server
echo "Starting CloudWatch Metrics MCP server..."
python -m awslabs.cloudwatch_mcp_server.server
