import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ITEMS_TABLE'])

# Encoder for Decimal (to deal with Price factor of items)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        response = table.scan()
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'], cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
