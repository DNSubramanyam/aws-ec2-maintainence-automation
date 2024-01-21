from pprint import pprint
def update_atom_status_to_db(event, context):
    # TODO implement
    import boto3
    from datetime import datetime

    con = boto3.session.Session()
    dynamodb = con.resource('dynamodb', region_name='us-east-1')

    table_name='maintenance-automation-table'
    db_table = dynamodb.Table(table_name)
    response = db_table.update_item(
        Key={
            'InstanceId': 'i-03fedc8397cfeb632'
        },
        UpdateExpression='set AppStopped = :val1, ServerStatus = :val3',
        ExpressionAttributeValues={
            ':val1': 'Yes',
            ':val2': 'start',
            ':val3': 'Checking',
            ':val4': datetime.now().strftime("%d-%m-%Y")
        },
        ConditionExpression= "begins_with(Process, :val2) AND begins_with(Timestamp, :val4)"
    )

    return response

if __name__ == "__main__":
    item = {
        'Name': 'Subbu',
        'Id': '23',
        'City': 'Bezawada'
    }
    event = {'to_write': item}
    pprint(update_atom_status_to_db(event, None))