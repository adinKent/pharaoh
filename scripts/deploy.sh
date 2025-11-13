#!/bin/bash

# Deploy script for Line webhook Lambda function
# Usage: ./scripts/deploy.sh [environment] [line-channel-secret] [line-channel-access-token]
# Line channel secret and access token arguments are optional when values already exist in SSM Parameter Store.

set -e

ENVIRONMENT=${1:-dev}
LINE_CHANNEL_SECRET=${2}
LINE_CHANNEL_ACCESS_TOKEN=${3}
AWS_PROFILE=${AWS_PROFILE:-default}
AWS_REGION=${AWS_REGION:-ap-east-2}

if [ -z "$LINE_CHANNEL_SECRET" ]; then
    echo "Line channel secret not provided via arguments. Attempting to read existing value from SSM Parameter Store..."
    LINE_CHANNEL_SECRET=$(aws --profile "$AWS_PROFILE" --region "$AWS_REGION" ssm get-parameter \
        --name "/pharaoh/$ENVIRONMENT/line/channel-secret" \
        --query Parameter.Value \
        --output text 2>/dev/null || echo "")
fi

if [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    echo "Line channel access token not provided via arguments. Attempting to read existing value from SSM Parameter Store..."
    LINE_CHANNEL_ACCESS_TOKEN=$(aws --profile "$AWS_PROFILE" --region "$AWS_REGION" ssm get-parameter \
        --name "/pharaoh/$ENVIRONMENT/line/channel-access-token" \
        --query Parameter.Value \
        --output text 2>/dev/null || echo "")
fi

if [ -z "$LINE_CHANNEL_SECRET" ] || [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    echo "Error: Line channel secret or access token not provided and not found in SSM Parameter Store."
    exit 1
fi

# Build the project
echo "Building the project..."
python -m pip install -r requirements-dev.txt
npm run build

echo "Deploying to environment: $ENVIRONMENT"

# Package the SAM application
echo "Packaging SAM application..."
sam build --profile $AWS_PROFILE --template-file infrastructure/template.yaml

# Deploy with parameters
echo "Deploying to AWS..."

# Check if stack exists and is in ROLLBACK_COMPLETE state
STACK_STATUS=$(aws --profile $AWS_PROFILE cloudformation describe-stacks --stack-name pharaoh-line-webhook-$ENVIRONMENT --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ]; then
    echo "Stack is in ROLLBACK_COMPLETE state. Deleting stack first..."
    aws --profile $AWS_PROFILE cloudformation delete-stack --stack-name pharaoh-line-webhook-$ENVIRONMENT
    echo "Waiting for stack deletion to complete..."
    aws --profile $AWS_PROFILE cloudformation wait stack-delete-complete --stack-name pharaoh-line-webhook-$ENVIRONMENT
    echo "Stack deleted successfully."
fi

sam deploy --profile $AWS_PROFILE \
    --stack-name pharaoh-line-webhook-$ENVIRONMENT \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset \
    --config-env $ENVIRONMENT \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        LineChannelSecret=$LINE_CHANNEL_SECRET \
        LineChannelAccessToken=$LINE_CHANNEL_ACCESS_TOKEN

# Get the webhook URL
echo "Getting webhook URL..."
WEBHOOK_URL=$(aws --profile $AWS_PROFILE --region "$AWS_REGION" cloudformation describe-stacks \
    --stack-name pharaoh-line-webhook-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
    --output text)

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "Environment: $ENVIRONMENT"
echo "Webhook URL: $WEBHOOK_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Copy the webhook URL above"
echo "2. Go to Line Developers Console (https://developers.line.biz/console/)"
echo "3. Select your Line Bot channel"
echo "4. Go to Messaging API settings"
echo "5. Set the webhook URL to: $WEBHOOK_URL"
echo "6. Enable webhook usage"
echo "7. Test your webhook by sending a message to your Line Bot"