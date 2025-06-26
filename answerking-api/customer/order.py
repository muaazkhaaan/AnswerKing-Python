import json
import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

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
        # Parse input
        body = json.loads(event['body'])
        items = body.get('items', [])

        if not items:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No items provided'})
            }

        # Convert items to use Decimal values
        cleaned_items = []
        total_price = Decimal('0.00')

        for item in items:
            price = Decimal(str(item['price']))
            quantity = Decimal(str(item['quantity']))
            total_price += price * quantity

            cleaned_items.append({
                'name': item['name'],
                'price': price,
                'quantity': quantity
            })

        # Auto-generate ID
        new_id = get_next_id()

        # Create new order item
        order = {
            'id': new_id,
            'items': cleaned_items,
            'total_price': total_price,
            'timestamp': datetime.now().strftime('%d/%m/%y-%H:%M'),
            'status': 'Pending'
        }

        # Store in DynamoDB
        table.put_item(Item=order)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Order created', 'order_id': order['id']})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }