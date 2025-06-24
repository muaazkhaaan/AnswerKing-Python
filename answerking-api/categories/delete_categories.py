import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CATEGORIES_TABLE'])

def lambda_handler(event, context):
    item_id = event['pathParameters'].get('id')

    if not item_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing item ID in path.'})
        }

    try:
        response = table.delete_item(
            Key={'id': item_id},
            ConditionExpression='attribute_exists(id)'  # Prevents deleting non-existent items
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Item {item_id} deleted successfully.'})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Item {item_id} not found.'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }