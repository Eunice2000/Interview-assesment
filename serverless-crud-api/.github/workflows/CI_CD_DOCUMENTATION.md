# CI/CD Pipeline Documentation

## Overview
This CI/CD pipeline automates the deployment of the serverless CRUD application using GitHub Actions.

## Pipeline Stages

### 1. Code Quality Checks
- **Trigger**: On every push and pull request
- **Checks**:
  - Python code linting with flake8
  - Code formatting with black
  - Syntax validation

### 2. Unit Tests
- **Trigger**: After successful code quality checks
- **Actions**:
  - Runs unit tests for Lambda functions
  - Uses pytest framework
  - Provides test coverage reporting

### 3. Deployment to Development
- **Trigger**: Push to `develop` branch
- **Actions**:
  - Builds SAM application
  - Deploys to AWS dev environment
  - Runs integration tests
  - Creates test item and verifies API

### 4. Deployment to Production
- **Trigger**: Push to `main` branch (after dev deployment)
- **Actions**:
  - Builds SAM application
  - Deploys to AWS prod environment
  - Includes rollback mechanism
  - Verifies deployment with health check

### 5. Notifications
- **Trigger**: Always runs
- **Actions**:
  - Success/failure notifications
  - Can be extended with Slack/Email

## Branch Strategy
- `main` → Production environment
- `develop` → Development environment
- Feature branches → Only run tests, no deployment

## GitHub Secrets Required

### Required Secrets (set in GitHub repository Settings > Secrets):
1. `AWS_ACCESS_KEY_ID` - AWS IAM user access key
2. `AWS_SECRET_ACCESS_KEY` - AWS IAM user secret key

### Optional Secrets (for notifications):
3. `SLACK_WEBHOOK_URL` - For Slack notifications
4. Email credentials for email notifications

## IAM Permissions
The IAM user used for deployment needs permissions for:
- CloudFormation (full access)
- Lambda (full access)
- API Gateway (full access)
- DynamoDB (full access)
- IAM (limited to role creation)
- S3 (for SAM artifacts)

## Manual Operations

### Trigger Manual Deployment:
```bash
# Push to develop branch for dev deployment
git push origin develop

# Push to main branch for prod deployment (after testing in dev)
git push origin main
