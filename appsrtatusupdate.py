def update_db_with_app_stopped(event,context):
    import boto3
    from datetime import datetime
    ssm = boto3.client('ssm', region_name='us-east-1')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    ins = event['ins_list']
    cid = event['CmdId']
    table_name = event['table_name']

    db_table = dynamodb.Table(table_name)

    for m in ins:
        is_app_stopped = ' '
        response = ssm.get_command_invocation(CommandId=cid, InstanceId=m)
        if response['Status'] == "Success" and response["StandardOutputContent"].strip() == "offline":
                print(f"updating success table for {m} with status {response['StandardOutputContent'].strip()}")
                is_app_stopped = 'Yes'
        else:
                is_app_stopped = 'No'

        response = db_table.scan(
            FilterExpression='#pk = :pk AND begins_with(#sk, :sk) AND begins_with(#fk, :fk)',
            ExpressionAttributeNames={'#pk': 'InstanceId', '#sk': 'Timestamp', '#fk': 'Process'},
            ExpressionAttributeValues={':pk': 'i-03fedc8397cfeb632', ':sk': datetime.now().strftime("%d-%m-%Y"), ':fk': event['process']}
        )

        items = response['Items']

        # Update the matching items
        for item in items:
            key = {
                'InstanceId': item['InstanceId'],  # Replace with your actual attribute names
                'Timestamp': item['Timestamp']
            }

            update_params = {
                'Key': key,
                'UpdateExpression': 'set AppStopped = :val1, ServerStatus = :val2',
                'ExpressionAttributeValues': {
                    ':val1': is_app_stopped,
                    ':val2': 'Checking'
                }
            }

            try:
                updated_item = db_table.update_item(**update_params)
                print("UpdateItem succeeded:", updated_item)
            except Exception as e:
                print("Error updating item:", e)


if __name__ == "__main__":
    event = {
    'CmdId' : "5c0378c6-3146-405f-9105-1324909e40f5",
    'ins_list' : ["i-03fedc8397cfeb632"],
    'table_name' : 'maintenance-automation-table',
    'process': 'start'
    }
    update_db_with_app_stopped(event, context=None)