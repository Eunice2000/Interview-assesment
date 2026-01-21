# Serverless CRUD API

A serverless CRUD API built with AWS SAM (Serverless Application Model) featuring automated CI/CD pipeline deployment.

## Features
- RESTful CRUD API (Create, Read, Update, Delete operations)
- AWS Lambda functions for business logic
- Amazon DynamoDB for data storage
- API Gateway for HTTP endpoints
- Automated CI/CD pipeline with GitHub Actions
- Infrastructure as Code with AWS SAM

## Architecture
```
API Gateway → Lambda Functions → DynamoDB Table
```

## Project Structure
```
serverless-crud-api/
├── src/functions/          # Lambda function source code
├── tests/                  # Test files (unit & integration)
├── .github/workflows/      # CI/CD pipeline definitions
├── template.yaml           # AWS SAM infrastructure definition
├── samconfig.toml          # SAM deployment configuration
└── README.md               # This file
```

## CI/CD Pipeline

### Overview
The GitHub Actions pipeline automatically builds, tests, and deploys the application to AWS staging environment on every push to the `feature/devops` branch.

### Pipeline Stages

#### 1. Code Quality Check
- **Linting**: Runs `flake8` on Python source code
- **Location**: Checks code in `serverless-crud-api/src/`

#### 2. Deployment
- **Build**: Uses AWS SAM to build Lambda functions with Docker container
- **Deploy**: Deploys to CloudFormation stack: `serverless-crud-api-staging`
- **Strategy**: Updates existing stack (no cleanup needed between deployments)

#### 3. Automated Testing
- **Smoke Test**: Verifies API endpoints are accessible after deployment
- **Future Work**: Comprehensive integration tests will be added

#### 4. Rollback Mechanism
- **Trigger**: Automatically rolls back if smoke tests fail
- **Method**: Uses CloudFormation rollback capability
- **Fallback**: Provides manual rollback instructions if auto-rollback fails

#### 5. Notifications
- **Slack**: Sends deployment status notifications to configured channel

## Setup Instructions

### Prerequisites
- AWS Account with appropriate permissions
- GitHub repository
- Python 3.10+
- AWS SAM CLI
- Docker (for local testing)

### 1. AWS Credentials Setup
Create an IAM user with these minimum permissions:
- `CloudFormation:*`
- `Lambda:*`
- `APIGateway:*`
- `DynamoDB:*`
- `IAM:PassRole`
- `S3:PutObject`

### 2. GitHub Secrets Configuration
Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM user secret key |
| `SLACK_BOT_TOKEN` | Slack bot token for notifications (optional) |

### 3. Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd serverless-crud-api

# Install dependencies
pip install -r requirements.txt

# Build the application
sam build --use-container

# Test locally
sam local invoke CreateItemFunction --event events/event.json
sam local start-api
```

### 4. Manual Deployment
```bash
# Deploy to AWS
sam deploy --stack-name serverless-crud-api-staging --parameter-overrides Stage=staging
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/items` | Create a new item |
| GET | `/items` | List all items |
| GET | `/items/{id}` | Get specific item |
| PUT | `/items/{id}` | Update an item |
| DELETE | `/items/{id}` | Delete an item |

## Testing

### Unit Tests
```bash
cd serverless-crud-api
python -m pytest tests/unit -v
```

### Integration Tests
Integration tests require a deployed stack:
```bash
export AWS_SAM_STACK_NAME="serverless-crud-api-staging"
python -m pytest tests/integration -v
```

### Pipeline Tests
The CI/CD pipeline includes:
1. **Code linting** with flake8
2. **Smoke tests** verifying API accessibility
3. **Future**: Comprehensive integration tests

## Monitoring and Troubleshooting

### CloudWatch Logs
```bash
# View Lambda function logs
sam logs --stack-name serverless-crud-api-staging --tail
```

### CloudFormation Status
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name serverless-crud-api-staging

# View deployment events
aws cloudformation describe-stack-events --stack-name serverless-crud-api-staging
```

### Manual Rollback
If automatic rollback fails:
```bash
aws cloudformation rollback-stack --stack-name serverless-crud-api-staging
```

## Environment Variables

### Pipeline Variables (set in workflow)
```yaml
AWS_REGION: us-east-1
STACK_NAME: serverless-crud-api-staging
```

### Application Parameters
- `Stage`: Deployment environment (staging/production)
- DynamoDB table name is auto-generated based on stage

## Cleanup

### Delete Stack
```bash
sam delete --stack-name serverless-crud-api-staging
```

### Manual Cleanup
If stack deletion fails, manually delete:
1. DynamoDB table: `items-staging`
2. Lambda functions: `*-staging`
3. API Gateway: `serverless-crud-api-staging`
4. CloudWatch log groups: `/aws/lambda/*-staging`

## Future Improvements
1. **Multi-environment support** (staging, production)
2. **Comprehensive integration tests**
3. **Security scanning** in pipeline
4. **Performance testing**
5. **Blue-green deployments**

## Troubleshooting Common Issues

### Deployment Failures
1. **IAM permissions**: Ensure IAM user has all required permissions
2. **Resource limits**: Check AWS service limits in your account
3. **Template errors**: Run `sam validate` before deployment

### API Gateway Issues
1. **Missing Authentication Token**: Check API Gateway stage deployment
2. **Timeout errors**: Verify Lambda function timeouts and VPC configuration

### Pipeline Failures
1. **GitHub Secrets**: Verify all required secrets are set
2. **AWS Region**: Ensure region matches your resources
3. **SAM CLI version**: Update to latest version

## Resources
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Lambda Python Guide](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
```

![alt text](stacks-running.png)
