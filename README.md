# CI/CD Pipeline Documentation

## Pipeline Overview
This pipeline automatically builds, deploys, and tests the serverless CRUD API to AWS staging environment.

## Pipeline Steps

### 1. Code Quality
- **Linting**: Runs `flake8` on Python source code
- **Location**: `serverless-crud-api/src/`

### 2. Deployment
- **Build**: Uses AWS SAM to build Lambda functions
- **Deploy**: Deploys to CloudFormation stack: `serverless-crud-api-staging`
- **Strategy**: Updates existing stack (no cleanup needed)

### 3. Automated Testing
- **Integration Tests**: Runs `tests/integration/test_api_gateway.py` if available
- **Fallback**: Performs basic CRUD operations test
- **Verification**: Tests all endpoints (Create, Read, Update, Delete)

### 4. Rollback Mechanism
- **Trigger**: Automatically rolls back if tests fail
- **Method**: Uses CloudFormation rollback capability
- **Manual**: Fallback to manual rollback if auto-rollback fails

## Required Environment Variables

### GitHub Secrets:
- `AWS_ACCESS_KEY_ID` - AWS IAM access key
- `AWS_SECRET_ACCESS_KEY` - AWS IAM secret key
- `SLACK_BOT_TOKEN` - Slack bot token for notifications

### Pipeline Variables (set in workflow):
- `AWS_REGION`: us-east-1
- `STACK_NAME`: serverless-crud-api-staging

## Manual Operations

### Deploy Manually:
```bash
cd serverless-crud-api
sam build
sam deploy --stack-name serverless-crud-api-staging --parameter-overrides Stage=staging
