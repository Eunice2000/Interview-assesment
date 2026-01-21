# Interview-assesment
# Serverless CRUD API

A serverless application built with AWS SAM implementing CRUD operations with API Gateway, Lambda, and DynamoDB.

## Architecture
- **API Gateway**: REST API endpoints
- **Lambda Functions**: Python 3.9 functions for CRUD operations
- **DynamoDB**: NoSQL database for data storage
- **IAM**: Least-privilege roles for Lambda functions

## Endpoints
- `POST /items` - Create new item
- `GET /items` - List all items (with optional ?category= filter)
- `GET /items/{itemId}` - Get item by ID
- `PUT /items/{itemId}` - Update item
- `DELETE /items/{itemId}` - Delete item

## Deployment

### Prerequisites
1. AWS CLI configured with credentials
2. AWS SAM CLI installed
3. Docker (for local testing)

### One-Command Deployment
```bash
# Deploy to dev environment
./scripts/deploy.sh dev

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production  
./scripts/deploy.sh prod
