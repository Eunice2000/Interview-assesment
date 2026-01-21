# GitHub Secrets Setup for CI/CD

## Required Secrets
Set these in your GitHub repository:
1. Go to Settings > Secrets and variables > Actions
2. Click "New repository secret"

## Secrets to Add:
1. **AWS_ACCESS_KEY_ID**
   - Your AWS IAM user access key
   - Used for deploying to AWS

2. **AWS_SECRET_ACCESS_KEY**
   - Your AWS IAM user secret key
   - Used for deploying to AWS

## IAM User Requirements
The IAM user needs these permissions:
- CloudFormation:*
- Lambda:*
- API Gateway:*
- DynamoDB:*
- IAM:PassRole, IAM:CreateRole
- S3:PutObject (for SAM deployment artifacts)
