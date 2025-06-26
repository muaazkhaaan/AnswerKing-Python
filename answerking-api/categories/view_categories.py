import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Categories')

def lambda_handler(event, context):
    try:
        response = table.scan()

        # Filter out the ID auto counter
        categories = [category for category in response['Items'] if category['id'] != 'counter']

        return {
            'statusCode': 200,
            'body': json.dumps(categories)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }