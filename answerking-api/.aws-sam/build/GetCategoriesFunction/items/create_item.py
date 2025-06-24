import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ITEMS_TABLE'])

def lambda_handler(event, context):
    body = json.loads(event['body'])

    item = {
        'id': body['id'],
        'name': body['name'],
        'price': Decimal(str(body['price'])),
        'category_id': body.get('category_id', None)
    }

    table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Item created'})
    }