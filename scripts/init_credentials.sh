#!/bin/bash

# Initialization script to store secrets in AWS Secrets Manager.
# Usage: ./scripts/init.sh [environment] [mongodb-username] [mongodb-password]

set -e

AWS_PROFILE=${AWS_PROFILE:-default}
AWS_REGION=${AWS_REGION:-ap-east-2}

ENVIRONMENT=${1:-dev}
MONGODB_USERNAME=${2}
MONGODB_PASSWORD=${3}

if [ -z "$MONGODB_USERNAME" ] || [ -z "$MONGODB_PASSWORD" ]; then
    echo "Error: MongoDB username and password must be provided."
    echo "Usage: ./scripts/init.sh [environment] [mongodb-username] [mongodb-password]"
    exit 1
fi

SECRET_NAME="/pharaoh/$ENVIRONMENT/mongodb/credentials"
SECRET_JSON=$(printf '{"username":"%s","password":"%s"}' "$MONGODB_USERNAME" "$MONGODB_PASSWORD")

echo "Checking for existing secret: $SECRET_NAME"

# Check if the secret already exists
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null 2>&1; then
    echo "Secret already exists. Updating its value..."
    aws secretsmanager put-secret-value \
        --secret-id "$SECRET_NAME" \
        --secret-string "$SECRET_JSON" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION"
    echo "Secret value updated successfully."
else
    echo "Secret does not exist. Creating a new secret..."
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "MongoDB credentials for the Pharaoh application in the $ENVIRONMENT environment." \
        --secret-string "$SECRET_JSON" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION"
    echo "Secret created successfully."
fi

echo ""
echo "✅ Initialization complete for environment: $ENVIRONMENT"