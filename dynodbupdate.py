import boto3
from pprint import pprint

def lambda_handler(event, context):
    # TODO implement
    con = boto3.session.Session()
    dynamodb = con.resource('dynamodb', region_name='us-east-1')

    table_name='maintenance-automation-table'
    db_table = dynamodb.Table(table_name)
    response = db_table.update_item(
        Key={
            'InstanceId': 'i-0ce263f9a90c1ab9d',
            'Timestamp': '13-01-2024'
        },
        UpdateExpression='set AppStopped = :val1, ServerStatus = :val3',
        ExpressionAttributeValues={
            ':val1': 'Yes',
            ':val2': 'start',
            ':val3': 'Checking'
        },
        ConditionExpression= "begins_with(Process, :val2)"
    )

    return response

if __name__ == "__main__":
    item = {
        'Name': 'Subbu',
        'Id': '23',
        'City': 'Bezawada'
    }
    event = {'to_write': item}
    pprint(lambda_handler(event, None))