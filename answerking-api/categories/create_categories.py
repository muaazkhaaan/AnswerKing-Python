import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CATEGORIES_TABLE'])

def get_next_id():
    # Increment counter atomically
    response = table.update_item(
        Key={'id': 'counter'},
        UpdateExpression='ADD current_id :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW'
    )
    return str(int(response['Attributes']['current_id']))

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Validate required fields except 'id'
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        # Auto-generate ID
        new_id = get_next_id()

        item = {
            'id': new_id,
            'category': body['category'],
            'description': body['description']
        }

        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Item created', 'id': new_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }