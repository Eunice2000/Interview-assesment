import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """Delete an item from DynamoDB"""
    try:
        if 'pathParameters' not in event or 'itemId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type: 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'itemId is required in path parameters'})
            }
        
        item_id = event['pathParameters']['itemId']
        
        # Check if item exists
        existing_response = table.get_item(Key={'itemId': item_id})
        if 'Item' not in existing_response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Item with ID {item_id} not found'})
            }
        
        # Delete item from DynamoDB
        table.delete_item(Key={'itemId': item_id})
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Item deleted successfully',
                'itemId': item_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
