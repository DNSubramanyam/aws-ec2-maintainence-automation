import boto3
import json
from pprint import pprint
from datetime import datetime

def get_fetch_tag(action):
    #current_day = datetime.now().weekday()
    current_day = 0
    fetch_tag = []
    tag_everyday = {"Env": 'Dev',"Schedule": "everyday"}
    tag_weekend = {"Env": 'Dev',"Schedule": "weekend"}

    if action == 'start':
        if current_day == 0:
            fetch_tag =  [{'Name': 'tag:maintenance-automation', 'Values':[json.dumps(tag_weekend), json.dumps(tag_everyday)]}]
        elif current_day in [5, 6]:
            fetch_tag = []
        else:
            fetch_tag =  [{'Name': 'tag:maintenance-automation', 'Values':[json.dumps(tag_everyday)]}]

    if action == 'stop':
        if current_day == 4:
            fetch_tag =  [{'Name': 'tag:maintenance-automation', 'Values':[json.dumps(tag_weekend), json.dumps(tag_everyday)]}]
        elif current_day in [5, 6]:
            fetch_tag = []
        else:
            fetch_tag =  [{'Name': 'tag:maintenance-automation', 'Values':[json.dumps(tag_everyday)]}]
    return fetch_tag
    
def lambda_handler(event, context):
    # TODO implement
    ec2 = boto3.client('ec2', region_name='us-east-1')
    asg = boto3.client('autoscaling', region_name='us-east-1')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table_name=event['TableName']
    db_table = dynamodb.Table(table_name)
    
    instance_list = []
    asg_list = []

    filter = get_fetch_tag(event['action'])

    if len(filter) > 0:
        ec2_response = ec2.describe_instances(Filters=filter)['Reservations']
        for b in ec2_response:
            for c in b['Instances']:
                instance_list.append(c['InstanceId'])

    if len(instance_list) > 0:
        asg_response = asg.describe_auto_scaling_instances(InstanceIds = instance_list)['AutoScalingInstances']
        for a in asg_response:
            asg_list.append(a['AutoScalingGroupName'])
            to_write={
                'InstanceId': a['InstanceId'],
                'Timestamp': datetime.now().strftime("%d-%m-%Y_%H:%M:%S"),
                'AutoScalingGroup': a['AutoScalingGroupName'],
            }
            db_table.put_item(Item=to_write)
        asg_list = list(set(asg_list))

    return {
        'statusCode': 200,
        'action': event['action'],
        'InstanceID': instance_list,
        'ASG_list': asg_list
    }

if __name__ == "__main__":
    event = {'action': 'start', 'environment': 'Dev', 'TableName': 'maintenance-automation-table'}
    print(lambda_handler(event, None))