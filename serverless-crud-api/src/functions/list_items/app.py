import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """List all items from DynamoDB"""
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        
        scan_params = {}
        
        if 'category' in query_params and query_params['category']:
            scan_params['FilterExpression'] = 'category = :category'
            scan_params['ExpressionAttributeValues'] = {
                ':category': query_params['category']
            }
        
        if 'limit' in query_params and query_params['limit']:
            try:
                scan_params['Limit'] = int(query_params['limit'])
            except ValueError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Limit must be a number'})
                }
        
        if scan_params:
            response = table.scan(**scan_params)
        else:
            response = table.scan()
        
        items = response.get('Items', [])
        
        result = {
            'message': 'Items retrieved successfully',
            'count': len(items),
            'items': items
        }
        
        if response.get('LastEvaluatedKey'):
            result['hasMore'] = True
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
