import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CATEGORIES_TABLE'])

def lambda_handler(event, context):
    try:
        # Ensure ID is provided in the path
        category_id = event['pathParameters'].get('id')
        if not category_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing category ID in path.'})
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

        if 'description' in body:
            update_expr.append('description = :description')
            expr_attr_values[':description'] = body['description']

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No valid fields to update.'})
            }

        # Build the whole expression
        update_params = {
            'Key': {'id': category_id},
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
                'message': f'Category {category_id} updated successfully.',
                'updated': response['Attributes']
            })
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Category {category_id} not found.'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }