# Pharaoh - Line Messaging API Webhook Handler

A serverless AWS Lambda function to handle webhook notifications from Line Messaging API. This project provides a complete infrastructure setup using AWS SAM (Serverless Application Model) for deploying a scalable and secure webhook handler written in Python.

## 🚀 Features

- **Secure Webhook Handling**: Validates Line webhook signatures to ensure authenticity
- **Comprehensive Event Support**: Handles all Line Messaging API event types (messages, follow/unfollow, postbacks, etc.)
- **AWS Infrastructure**: Complete CloudFormation/SAM template with API Gateway, Lambda, and monitoring
- **Environment Management**: Support for dev, staging, and production environments
- **Local Development**: SAM local development environment for testing
- **Error Handling**: Robust error handling with CloudWatch alarms and dead letter queues
- **Testing**: Pytest test suite with comprehensive coverage
- **CI/CD Ready**: Deployment scripts and configuration for automated deployments
- **Python 3.11**: Modern Python with type hints and async support

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/) (v3.11 or later)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [Line Developer Account](https://developers.line.biz/)

## 🏗️ Project Structure

```
pharaoh/
├── src/
│   ├── app.py               # Main Lambda function
│   └── requirements.txt     # Lambda dependencies
├── tests/
│   ├── __init__.py          # Test package
│   └── test_app.py          # Unit tests
├── infrastructure/
│   └── template.yaml        # SAM CloudFormation template
├── scripts/
│   ├── deploy.sh           # Unix deployment script
│   ├── deploy.bat          # Windows deployment script
│   └── local.sh            # Local development script
├── package.json            # Project metadata and scripts
├── requirements-dev.txt    # Development dependencies
├── samconfig.toml          # SAM deployment configuration
├── pytest.ini             # Pytest configuration
├── setup.cfg               # Flake8 configuration
├── pyproject.toml          # Black and isort configuration
├── .env.example           # Environment variables template
├── local-env.json         # Local development environment
└── README.md              # This file
```

## ⚙️ Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/your-username/pharaoh-line-webhook.git
cd pharaoh-line-webhook

# Install Python dependencies
python -m pip install -r requirements-dev.txt
```

### 2. Configure Line Messaging API

1. Go to [Line Developers Console](https://developers.line.biz/console/)
2. Create a new channel or select an existing one
3. Go to the "Messaging API" tab
4. Note down your **Channel Secret** and **Channel Access Token**

### 3. Set Up Environment Variables

```bash
# Copy the environment template
cp .env.example .env.local

# Edit .env.local with your actual Line credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_channel_access_token
```

### 4. Configure AWS

Ensure your AWS CLI is configured with appropriate credentials:

```bash
aws configure
```

The deployment requires the following AWS permissions:
- CloudFormation stack creation/updates
- Lambda function management
- API Gateway management
- CloudWatch logs and alarms
- SQS queue management
- S3 bucket access (for deployment artifacts)

## 🚀 Deployment

### Quick Deployment

Use the deployment script for easy deployment:

**Unix/Linux/macOS:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh dev "your-channel-secret" "your-channel-access-token"
```

**Windows:**
```cmd
scripts\deploy.bat dev "your-channel-secret" "your-channel-access-token"
```

### Manual Deployment

```bash
# Build and test
npm run build

# Package the SAM application
sam build --template-file infrastructure/template.yaml

# Deploy to dev environment
sam deploy --config-env dev \
    --parameter-overrides \
        Environment=dev \
        LineChannelSecret="your-channel-secret" \
        LineChannelAccessToken="your-channel-access-token"
```

### Deploy to Different Environments

```bash
# Development
python -m pip install -r requirements-dev.txt
npm run deploy:dev

# Staging
npm run deploy:staging

# Production
npm run deploy:prod
```

## 🧪 Local Development

### Start Local API Gateway

```bash
# Start local development server
chmod +x scripts/local.sh
./scripts/local.sh
```

The webhook will be available at: `http://localhost:3000/webhook`

### Test Local Webhook

```bash
# Test with curl
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -H "x-line-signature: test-signature" \
  -d '{"events":[]}'
```

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test file
python -m pytest tests/test_app.py -v

# Lint code
flake8 src/ tests/

# Format code
black src/ tests/
isort src/ tests/
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINE_CHANNEL_SECRET` | Line Messaging API Channel Secret | Yes |
| `LINE_CHANNEL_ACCESS_TOKEN` | Line Messaging API Channel Access Token | Yes |
| `ENVIRONMENT` | Environment name (dev/staging/prod) | Yes |

### SAM Configuration

The `samconfig.toml` file contains configuration for different environments:

- **dev**: Development environment with detailed logging
- **staging**: Staging environment for testing
- **prod**: Production environment with optimized settings

## 📡 Webhook Configuration

After deployment, configure your Line bot webhook:

1. Copy the webhook URL from the deployment output
2. Go to [Line Developers Console](https://developers.line.biz/console/)
3. Select your channel → Messaging API
4. Set **Webhook URL** to your deployed endpoint
5. Enable **Use webhook**
6. Verify the webhook (should return success)

### Webhook URL Format
```
https://{api-id}.execute-api.{region}.amazonaws.com/{environment}/webhook
```

## 📱 Supported Line Events

The webhook handler supports all Line Messaging API event types:

### Message Events
- **Text messages**: Echo functionality (customize in `handleMessageEvent`)
- **Image messages**: File ID logging
- **Video messages**: File ID logging
- **Audio messages**: File ID logging
- **File messages**: File ID logging
- **Location messages**: Coordinate processing
- **Sticker messages**: Package and sticker ID logging

### Account Events
- **Follow**: User adds bot as friend
- **Unfollow**: User removes bot
- **Join**: Bot joins group/room
- **Leave**: Bot leaves group/room
- **Member joined**: Members join group/room
- **Member left**: Members leave group/room

### Interaction Events
- **Postback**: Rich menu and template interactions
- **Beacon**: LINE Beacon interactions
- **Account Link**: Account linking results
- **Things**: LINE Things device events

## 🛠️ Customization

### Adding Business Logic

Modify the event handlers in `src/app.py`:

```python
def handle_message_event(event: Dict[str, Any]) -> None:
    """Handle message events"""
    message = event.get('message', {})
    source = event.get('source', {})
    reply_token = event.get('replyToken')
    
    if message.get('type') == 'text':
        text_message = message.get('text')
        
        # Add your custom logic here
        response = process_user_message(text_message)
        
        send_reply_message(reply_token, {
            'type': 'text',
            'text': response
        })

def process_user_message(text: str) -> str:
    """Process user message and return response"""
    # Implement your business logic here
    if 'hello' in text.lower():
        return 'Hello! How can I help you today?'
    elif 'weather' in text.lower():
        return 'I can help you with weather information!'
    else:
        return f'You said: {text}'
```

### Database Integration

Add database operations by importing boto3:

```python
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

def save_user_message(user_id: str, message: str) -> None:
    """Save user message to DynamoDB"""
    table = dynamodb.Table('UserMessages')
    
    try:
        table.put_item(
            Item={
                'userId': user_id,
                'message': message,
                'timestamp': int(time.time())
            }
        )
        logger.info(f'Saved message for user {user_id}')
    except ClientError as e:
        logger.error(f'Error saving message: {e}')

def get_user_messages(user_id: str) -> List[Dict[str, Any]]:
    """Get user messages from DynamoDB"""
    table = dynamodb.Table('UserMessages')
    
    try:
        response = table.query(
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f'Error getting messages: {e}')
        return []
```

### Adding External APIs

Install additional dependencies and add API calls:

```bash
# Add to requirements-dev.txt
httpx==0.25.0
aiohttp==3.8.5
```

```python
import httpx
import asyncio

async def call_external_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """Call external API asynchronously"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.example.com/process',
            json=data,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

def handle_message_event(event: Dict[str, Any]) -> None:
    """Handle message with external API call"""
    message = event.get('message', {})
    
    if message.get('type') == 'text':
        # Process with external API
        result = asyncio.run(call_external_api({
            'text': message.get('text'),
            'user_id': event.get('source', {}).get('userId')
        }))
        
        send_reply_message(event.get('replyToken'), {
            'type': 'text',
            'text': result.get('response', 'Processing completed')
        })
```

## 📊 Monitoring

The deployment includes CloudWatch monitoring:

### Alarms
- **Lambda Errors**: Triggers when error count exceeds threshold
- **Lambda Duration**: Triggers when execution time is too long
- **API Gateway 4xx**: Client error monitoring
- **API Gateway 5xx**: Server error monitoring

### Logs
- **Lambda Logs**: `/aws/lambda/line-webhook-{environment}`
- **API Gateway Logs**: `/aws/apigateway/line-webhook-api-{environment}`

### View Logs

```bash
# View Lambda logs
npm run logs

# Or use AWS CLI
aws logs tail /aws/lambda/line-webhook-dev --follow
```

## 🔒 Security

### Webhook Security
- **Signature Verification**: All webhooks are verified using HMAC-SHA256
- **HTTPS Only**: API Gateway enforces HTTPS
- **CORS Configuration**: Properly configured CORS headers

### AWS Security
- **IAM Roles**: Least privilege access for Lambda function
- **VPC**: Optional VPC configuration (uncomment in template.yaml)
- **Environment Variables**: Sensitive data stored securely

### Best Practices
- Regularly rotate Line channel credentials
- Monitor CloudWatch alarms
- Review Lambda function permissions
- Use AWS Secrets Manager for production credentials

## 🐛 Troubleshooting

### Common Issues

#### 1. Webhook Verification Failed
```
Error: Invalid signature
```
**Solution**: Check that your `LINE_CHANNEL_SECRET` is correct

#### 2. Missing Environment Variables
```
Error: Server configuration error
```
**Solution**: Ensure all required environment variables are set

#### 3. Deployment Failed
```
Error: Unable to upload artifact
```
**Solution**: Check AWS credentials and S3 bucket permissions

#### 4. Local Development Issues
```
Error: Template does not exist
```
**Solution**: Ensure you're running from the project root directory

### Debug Mode

Enable debug logging:

```bash
export SAM_CLI_DEBUG=1
sam local start-api
```

### Webhook Testing

Test webhook signature verification:

```bash
# Generate valid signature
echo -n '{"events":[]}' | openssl dgst -sha256 -hmac "your-channel-secret" -binary | base64

# Test with curl
curl -X POST https://your-api-url/webhook \
  -H "Content-Type: application/json" \
  -H "x-line-signature: GENERATED_SIGNATURE" \
  -d '{"events":[]}'
```

## 📈 Performance Optimization

### Lambda Optimization
- **Memory**: Adjust memory allocation based on usage patterns
- **Timeout**: Set appropriate timeout values
- **Concurrency**: Configure reserved concurrency for predictable performance

### Cost Optimization
- **CloudWatch Logs**: Adjust retention periods
- **API Gateway**: Consider caching for frequently accessed endpoints
- **Lambda**: Use ARM-based processors for better price/performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Use type hints for better code documentation
- Write tests for new features
- Update documentation
- Test in local environment before submitting
- Use Black for code formatting
- Use isort for import sorting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Line Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Line Developer Console](https://developers.line.biz/console/)

## 📞 Support

For support and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review [Line Messaging API documentation](https://developers.line.biz/en/docs/)
3. Open an issue in this repository
4. Contact the maintainer

---

**Happy coding! 🎉**