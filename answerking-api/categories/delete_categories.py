import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CATEGORIES_TABLE'])

def lambda_handler(event, context):
    category_id = event['pathParameters'].get('id')

    if not category_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing category ID in path.'})
        }

    try:
        table.delete_item(
            Key={'id': category_id},
            ConditionExpression='attribute_exists(id)'  # Prevents deleting non-existent categories
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Category {category_id} deleted successfully.'})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Category {category_id} not found.'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }