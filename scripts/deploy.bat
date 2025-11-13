@echo off
REM Deploy script for Line webhook Lambda function (Windows)
REM Usage: scripts\deploy.bat [environment] [line-channel-secret] [line-channel-access-token]
REM Line channel secret and access token arguments are optional when values already exist in SSM Parameter Store.

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev

set LINE_CHANNEL_SECRET=%2
set LINE_CHANNEL_ACCESS_TOKEN=%3

set AWS_PROFILE=%AWS_PROFILE%
if "%AWS_PROFILE%"=="" set AWS_PROFILE=default

set AWS_REGION=%AWS_REGION%
if "%AWS_REGION%"=="" set AWS_REGION=ap-east-2

if "%LINE_CHANNEL_SECRET%"=="" (
    echo Line channel secret not provided via arguments. Attempting to read existing value from SSM Parameter Store...
    set "LINE_CHANNEL_SECRET="
    for /f "usebackq tokens=*" %%i in (`aws --profile %AWS_PROFILE% --region %AWS_REGION% ssm get-parameter --name "/pharaoh/%ENVIRONMENT%/line/channel-secret" --query "Parameter.Value" --output text 2^>nul`) do set LINE_CHANNEL_SECRET=%%i
)

if "%LINE_CHANNEL_ACCESS_TOKEN%"=="" (
    echo Line channel access token not provided via arguments. Attempting to read existing value from SSM Parameter Store...
    set "LINE_CHANNEL_ACCESS_TOKEN="
    for /f "usebackq tokens=*" %%i in (`aws --profile %AWS_PROFILE% --region %AWS_REGION% ssm get-parameter --name "/pharaoh/%ENVIRONMENT%/line/channel-access-token" --query "Parameter.Value" --output text 2^>nul`) do set LINE_CHANNEL_ACCESS_TOKEN=%%i
)

if "%LINE_CHANNEL_SECRET%"=="" (
    echo Error: Line channel secret not provided and not found in SSM Parameter Store.
    exit /b 1
)

if "%LINE_CHANNEL_ACCESS_TOKEN%"=="" (
    echo Error: Line channel access token not provided and not found in SSM Parameter Store.
    exit /b 1
)

echo Deploying to environment: %ENVIRONMENT%

REM Build the project
echo Building the project...
python -m pip install -r requirements-dev.txt
call npm run build
if !errorlevel! neq 0 exit /b !errorlevel!

REM Package the SAM application
echo Packaging SAM application...
call sam build --profile %AWS_PROFILE% --template-file infrastructure/template.yaml
if !errorlevel! neq 0 exit /b !errorlevel!

REM Deploy with parameters
echo Deploying to AWS...
call sam deploy --profile %AWS_PROFILE% ^
    --config-env %ENVIRONMENT% ^
    --parameter-overrides Environment=%ENVIRONMENT% LineChannelSecret=%LINE_CHANNEL_SECRET% LineChannelAccessToken=%LINE_CHANNEL_ACCESS_TOKEN%
if !errorlevel! neq 0 exit /b !errorlevel!

REM Get the webhook URL
echo Getting webhook URL...
for /f "tokens=*" %%i in ('aws --profile %AWS_PROFILE% --region %AWS_REGION% cloudformation describe-stacks --stack-name pharaoh-line-webhook-%ENVIRONMENT% --query "Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue" --output text') do set WEBHOOK_URL=%%i

echo.
echo ✅ Deployment completed successfully!
echo.
echo 📋 Deployment Summary:
echo Environment: %ENVIRONMENT%
echo Webhook URL: %WEBHOOK_URL%
echo.
echo 🔧 Next Steps:
echo 1. Copy the webhook URL above
echo 2. Go to Line Developers Console (https://developers.line.biz/console/)
echo 3. Select your Line Bot channel
echo 4. Go to Messaging API settings
echo 5. Set the webhook URL to: %WEBHOOK_URL%
echo 6. Enable webhook usage
echo 7. Test your webhook by sending a message to your Line Bot

endlocal