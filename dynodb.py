import boto3

def lambda_handler(event, context):
    # TODO implement
    con = boto3.session.Session()
    dynamodb = con.resource('dynamodb', region_name='us-east-1')

    table_name='test-table'
    db_table = dynamodb.Table(table_name)
    response = db_table.put_item(Item=event['to_write'])

    return {
        'statusCode': 200,
        'response': response
    }

if __name__ == "__main__":
    item = {
        'Name': 'Subbu',
        'Id': '23',
        'City': 'Bezawada'
    }
    event = {'to_write': item}
    print(lambda_handler(event, None))