#!/bin/bash

# Local development script for Line webhook Lambda function

set -e

echo "Starting local development environment..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    echo "Please install Python 3.11 or later"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "Error: AWS SAM CLI is not installed"
    echo "Please install SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Creating .env.local from template..."
    cp .env.example .env.local
    echo "Please update .env.local with your Line channel credentials"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install -r requirements-dev.txt

# Load environment variables
source .env.local

# Validate required environment variables
if [ -z "$LINE_CHANNEL_SECRET" ] || [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    echo "Error: Please set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN in .env.local"
    exit 1
fi

# Build the project
echo "Building the project..."
python -m pytest tests/ -v
flake8 src/ tests/

# Start local API Gateway
echo "Starting local API Gateway on port 3000..."
echo "Webhook endpoint will be available at: http://localhost:3000/webhook"
echo ""
echo "To test the webhook, you can use:"
echo "curl -X POST http://localhost:3000/webhook \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'x-line-signature: test-signature' \\"
echo "  -d '{\"events\":[]}'"
echo ""
echo "Press Ctrl+C to stop the local server"

sam local start-api \
    --template-file infrastructure/template.yaml \
    --env-vars local-env.json \
    --port 3000