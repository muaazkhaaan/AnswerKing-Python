import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ITEMS_TABLE'])

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

        # Only allow updating these fields
        update_expr = []
        expr_attr_values = {}

        if 'name' in body:
            update_expr.append('name = :name')
            expr_attr_values[':name'] = body['name']
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

        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression='SET ' + ', '.join(update_expr),
            ExpressionAttributeValues=expr_attr_values,
            ConditionExpression='attribute_exists(id)',  # Ensure item exists
            ReturnValues='UPDATED_NEW'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Item {item_id} updated successfully.',
                'updated': response['Attributes']
            })
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