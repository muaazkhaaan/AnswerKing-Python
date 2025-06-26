import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table('Orders')
items_table = dynamodb.Table('Items')

# Encoder for Decimal (for response if needed)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def get_next_id():
    response = orders_table.update_item(
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
        input_items = body.get('items', [])

        if not input_items:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No items provided'})
            }

        # Get valid items from Items table
        items_data = items_table.scan()
        valid_items = {
            item['name']: item
            for item in items_data['Items']
            if item['id'] != 'counter'
        }

        validated_items = []

        for item in input_items:
            name = item.get('name')
            quantity = item.get('quantity')
            price = item.get('price')

            # Check item exists
            if name not in valid_items:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Item "{name}" not found in Items table'})
                }

            # Check price matches
            expected_price = str(valid_items[name]['price'])
            if str(price) != expected_price:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Incorrect price for item "{name}". Expected: {expected_price}'})
                }

            validated_items.append({
                'name': name,
                'price': Decimal(str(price)),
                'quantity': Decimal(str(quantity))
            })

        # Calculate total
        total_price = sum(item['price'] * item['quantity'] for item in validated_items)

        # Create order record
        order = {
            'id': get_next_id(),
            'items': validated_items,
            'total_price': total_price,
            'timestamp': datetime.now().strftime('%d/%m/%y-%H:%M'),
            'status': 'Pending'
        }

        # Store in DynamoDB
        orders_table.put_item(Item=order)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Order created',
                'order_id': order['id']
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }