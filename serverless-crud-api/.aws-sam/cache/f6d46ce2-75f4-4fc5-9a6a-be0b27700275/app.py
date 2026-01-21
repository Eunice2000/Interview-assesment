import json
import os
import boto3
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """Update an existing item in DynamoDB"""
    try:
        if 'pathParameters' not in event or 'itemId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'itemId is required in path parameters'})
            }
        
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        item_id = event['pathParameters']['itemId']
        body = json.loads(event['body'])
        
        # Check if item exists
        existing_response = table.get_item(Key={'itemId': item_id})
        if 'Item' not in existing_response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Item with ID {item_id} not found'})
            }
        
        # Build update expression
        update_expression = "SET updatedAt = :updatedAt"
        expression_attribute_values = {':updatedAt': datetime.utcnow().isoformat()}
        
        allowed_fields = ['name', 'description', 'category']
        for field in allowed_fields:
            if field in body and body[field] is not None:
                update_expression += f", {field} = :{field}"
                expression_attribute_values[f':{field}'] = body[field]
        
        # Update item in DynamoDB
        response = table.update_item(
            Key={'itemId': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Item updated successfully',
                'item': response['Attributes']
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
