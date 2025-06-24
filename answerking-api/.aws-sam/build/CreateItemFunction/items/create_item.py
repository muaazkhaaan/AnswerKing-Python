import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ITEMS_TABLE'])

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Validate required fields
        required_fields = ['id', 'name', 'price', 'category']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        item = {
            'id': body['id'],
            'name': body['name'],
            'price': Decimal(str(body['price'])),
            'category': body['category']
        }

        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Item created'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }