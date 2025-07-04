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
        # Ensure ID is provided in the path
        item_id = event['pathParameters'].get('id')
        if not item_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing item ID in path.'})
            }

        body = json.loads(event['body'])

        # Update builder
        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}

        # name is reserved in DynamoDB need to manage safely
        if 'name' in body:
            update_expr.append('#name = :name')
            expr_attr_values[':name'] = body['name']
            expr_attr_names['#name'] = 'name'

        # price must be in Decimal format
        if 'price' in body:
            update_expr.append('price = :price')
            expr_attr_values[':price'] = Decimal(str(body['price']))

        if 'category' in body:
            update_expr.append('category = :category')
            expr_attr_values[':category'] = body['category']

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No valid fields to update.'})
            }

        # Build the whole expression
        update_params = {
            'Key': {'id': item_id},
            'UpdateExpression': 'SET ' + ', '.join(update_expr),
            'ExpressionAttributeValues': expr_attr_values,
            'ConditionExpression': 'attribute_exists(id)',
            'ReturnValues': 'UPDATED_NEW'
        }

        if expr_attr_names:
            update_params['ExpressionAttributeNames'] = expr_attr_names

        # Perform update
        response = table.update_item(**update_params)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Item {item_id} updated successfully.',
                'updated': response['Attributes']
            }, cls=DecimalEncoder)
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Item {item_id} not found.'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }