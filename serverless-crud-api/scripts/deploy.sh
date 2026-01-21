#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if stage parameter is provided
STAGE=${1:-dev}

# Validate stage
if [[ ! $STAGE =~ ^(dev|staging|prod)$ ]]; then
    print_error "Stage must be one of: dev, staging, prod"
    exit 1
fi

# AWS Region
REGION=${AWS_REGION:-us-east-1}
print_info "Using AWS Region: $REGION"

# Stack name
STACK_NAME="serverless-crud-api-$STAGE"
print_info "Deploying stack: $STACK_NAME"

# Validate AWS credentials
print_info "Validating AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_error "AWS credentials not configured or invalid"
    exit 1
fi

print_info "AWS credentials validated successfully"

# Check if SAM CLI is installed
print_info "Checking SAM CLI installation..."
sam --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_error "SAM CLI not installed. Please install it first."
    exit 1
fi

print_info "SAM CLI version: $(sam --version)"

# Build SAM application
print_info "Building SAM application..."
sam build \
    --use-container \
    --parallel

if [ $? -ne 0 ]; then
    print_error "SAM build failed"
    exit 1
fi

print_info "SAM build completed successfully"

# Deploy SAM application
print_info "Deploying to $STAGE environment..."
print_info "Note: This may take 5-10 minutes..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --parameter-overrides Stage=$STAGE \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --no-fail-on-empty-changeset \
    --no-confirm-changeset

if [ $? -ne 0 ]; then
    print_error "SAM deployment failed"
    exit 1
fi

print_info "Deployment completed successfully!"

# Get stack outputs
print_info "Retrieving stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "Stacks[0].Outputs" \
    --output json 2>/dev/null || echo "[]")

if [ "$OUTPUTS" != "[]" ]; then
    print_info "\n=== Stack Outputs ==="
    echo $OUTPUTS | python3 -m json.tool
fi

# Get API endpoint
API_URL=$(echo $OUTPUTS | python3 -c "
import sys,json
try:
    data=json.load(sys.stdin)
    for o in data:
        if o['OutputKey']=='ApiGatewayUrl':
            # Remove trailing slash if present
            url = o['OutputValue']
            if url.endswith('/'):
                url = url[:-1]
            print(url)
except:
    pass
" 2>/dev/null || echo "")

if [ ! -z "$API_URL" ]; then
    print_info "\n=== API Endpoint ==="
    echo "$API_URL"
    
    print_info "\n=== Test Commands ==="
    echo "Create item:"
    echo "curl -X POST $API_URL/items \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"name\":\"Test Item\",\"description\":\"Test Description\"}'"
    
    echo -e "\nList items:"
    echo "curl $API_URL/items"
    
    # Wait a moment for API to be fully ready
    print_info "\nWaiting 30 seconds for API to be fully ready..."
    sleep 30
    
    # Create a test item with simpler HTTP code extraction
    print_info "Creating a test item..."
    
    # Create a temporary file for the response
    TEMP_FILE=$(mktemp)
    
    # Make the request and capture full response
    HTTP_CODE=$(curl -s -o "$TEMP_FILE" -w "%{http_code}" -X POST "$API_URL/items" \
        -H "Content-Type: application/json" \
        -d '{"name":"Initial Test Item","description":"Created by deployment script","category":"test"}')
    
    if [ "$HTTP_CODE" = "201" ]; then
        RESPONSE_BODY=$(cat "$TEMP_FILE")
        ITEM_ID=$(echo "$RESPONSE_BODY" | python3 -c "
import sys,json
try:
    data=json.load(sys.stdin)
    print(data.get('itemId', ''))
except:
    pass
" 2>/dev/null || echo "")
        
        if [ ! -z "$ITEM_ID" ]; then
            print_info "Test item created with ID: $ITEM_ID"
            echo -e "\nGet test item:"
            echo "curl $API_URL/items/$ITEM_ID"
        else
            print_warn "Created item but could not extract itemId"
        fi
    else
        print_warn "Could not create test item (HTTP $HTTP_CODE)"
        print_warn "Response body:"
        cat "$TEMP_FILE" 2>/dev/null || echo "No response body"
    fi
    
    # Clean up temp file
    rm -f "$TEMP_FILE"
fi

print_info "\n=== Monitoring Links ==="
print_info "CloudFormation Console: https://$REGION.console.aws.amazon.com/cloudformation/home?region=$REGION#/stacks/stackinfo?stackId=$STACK_NAME"
print_info "API Gateway Console: https://$REGION.console.aws.amazon.com/apigateway/home?region=$REGION"
print_info "Lambda Console: https://$REGION.console.aws.amazon.com/lambda/home?region=$REGION"
print_info "DynamoDB Console: https://$REGION.console.aws.amazon.com/dynamodb/home?region=$REGION"

print_info "\n Deployment to $STAGE completed! "
print_info "You can now test your API with the commands above."
