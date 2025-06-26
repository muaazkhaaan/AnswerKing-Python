import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Items')

# Encoder for Decimal (to deal with Price factor of items)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)
    
def lambda_handler(event, context):
    try:
        # Get category name from query - don't allow empty strings
        category_name = event.get('pathParameters', {}).get('category', '').strip()

        if not category_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing or invalid category parameter'})
            }

        response = table.scan()

        # Filter out the ID auto counter and only pick the selected category items
        filtered = [
            item for item in response['Items']
            if item['id'] != 'counter' and item.get('category') == category_name
        ]

        # If nothing has been picked up = error
        if not filtered:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No items found for category "{category_name}"'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(filtered, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }