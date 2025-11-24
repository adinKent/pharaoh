#!/bin/bash

# Initialization script to store secrets in AWS Secrets Manager.
# Usage:
#   Update MongoDB credentials:
#     ./scripts/init.sh --env dev --mongo-user <user> --mongo-password <pass>
#   Update LINE credentials:
#     ./scripts/init.sh --env dev --line-channel-secret <secret> --line-channel-access-token <token>
#   Update both:
#     ./scripts/init.sh --env dev --mongo-user <user> --mongo-password <password> --line-channel-secret <secret> --line-channel-access-token <token>

set -e

AWS_PROFILE=${AWS_PROFILE:-default}
AWS_REGION=${AWS_REGION:-ap-east-2}

# Default values
ENVIRONMENT="dev"
MONGODB_USERNAME=""
MONGODB_PASSWORD=""
LINE_CHANNEL_SECRET=""
LINE_CHANNEL_ACCESS_TOKEN=""
GEMINI_API_KEY=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --env)
        ENVIRONMENT="$2"
        shift 2
        ;;
        --mongo-user)
        MONGODB_USERNAME="$2"
        shift 2
        ;;
        --mongo-password)
        MONGODB_PASSWORD="$2"
        shift 2
        ;;
        --line-channel-secret)
        LINE_CHANNEL_SECRET="$2"
        shift 2
        ;;
        --line-channel-access-token)
        LINE_CHANNEL_ACCESS_TOKEN="$2"
        shift 2
        ;;
        --gemini-api-key)
        GEMINI_API_KEY="$2"
        shift 2
        ;;
        *)    # unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

if [ -z "$MONGODB_USERNAME" ] && [ -z "$MONGODB_PASSWORD" ] && [ -z "$LINE_CHANNEL_SECRET" ] && [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: No credentials provided to update."
    echo "Usage: ./scripts/init.sh [--env <env>] [--mongo-user <user> --mongo-password <pass>] [--line-channel-secret <secret> --line-channel-access-token <token>]"
    exit 1
fi

if [ -n "$MONGODB_USERNAME" ] || [ -n "$MONGODB_PASSWORD" ]; then
    if [ -z "$MONGODB_USERNAME" ] || [ -z "$MONGODB_PASSWORD" ]; then
        echo "Error: Both --mongo-user and --mongo-password must be provided to update MongoDB credentials."
        exit 1
    fi
    
    SECRET_NAME="/pharaoh/$ENVIRONMENT/mongodb/credentials"
    SECRET_JSON=$(printf '{"username":"%s","password":"%s"}' "$MONGODB_USERNAME" "$MONGODB_PASSWORD")

    echo "Checking for existing MongoDB secret: $SECRET_NAME"

    if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "MongoDB secret already exists. Updating its value..."
        aws secretsmanager put-secret-value --secret-id "$SECRET_NAME" --secret-string "$SECRET_JSON" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "MongoDB secret value updated successfully."
    else
        echo "MongoDB secret does not exist. Creating a new secret..."
        aws secretsmanager create-secret --name "$SECRET_NAME" --description "MongoDB credentials for Pharaoh in $ENVIRONMENT" --secret-string "$SECRET_JSON" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "MongoDB secret created successfully."
    fi
fi

if [ -n "$LINE_CHANNEL_SECRET" ]; then
    SECRET_NAME="/pharaoh/$ENVIRONMENT/line/channel-secret"
    echo "Checking for existing LINE Channel Secret: $SECRET_NAME"
    if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "LINE Channel Secret already exists. Updating its value..."
        aws secretsmanager put-secret-value --secret-id "$SECRET_NAME" --secret-string "$LINE_CHANNEL_SECRET" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "LINE Channel Secret value updated successfully."
    else
        echo "LINE Channel Secret does not exist. Creating a new secret..."
        aws secretsmanager create-secret --name "$SECRET_NAME" --description "LINE Channel Secret for Pharaoh in $ENVIRONMENT" --secret-string "$LINE_CHANNEL_SECRET" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "LINE Channel Secret created successfully."
    fi
fi

if [ -n "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    SECRET_NAME="/pharaoh/$ENVIRONMENT/line/channel-access-token"
    echo "Checking for existing LINE Access Token: $SECRET_NAME"

    if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "LINE Access Token already exists. Updating its value..."
        aws secretsmanager put-secret-value --secret-id "$SECRET_NAME" --secret-string "$LINE_CHANNEL_ACCESS_TOKEN" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "LINE Access Token value updated successfully."
    else
        echo "LINE Access Token does not exist. Creating a new secret..."
        aws secretsmanager create-secret --name "$SECRET_NAME" --description "LINE Channel Access Token for Pharaoh in $ENVIRONMENT" --secret-string "$LINE_CHANNEL_ACCESS_TOKEN" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "LINE Access Token created successfully."
    fi
fi

if [ -n "$GEMINI_API_KEY" ]; then
    SECRET_NAME="/pharaoh/$ENVIRONMENT/google/gemini-api-key"
    echo "Checking for existing Google Gemini API key: $SECRET_NAME"

    if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "GEMINI API key already exists. Updating its value..."
        aws secretsmanager put-secret-value --secret-id "$SECRET_NAME" --secret-string "$GEMINI_API_KEY" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "GEMINI API key value updated successfully."
    else
        echo "GEMINI API key does not exist. Creating a new secret..."
        aws secretsmanager create-secret --name "$SECRET_NAME" --description "GEMINI API key for Pharaoh in $ENVIRONMENT" --secret-string "$GEMINI_API_KEY" --profile "$AWS_PROFILE" --region "$AWS_REGION"
        echo "GEMINI API key created successfully."
    fi
fi

echo ""
echo "✅ Initialization complete for environment: $ENVIRONMENT"