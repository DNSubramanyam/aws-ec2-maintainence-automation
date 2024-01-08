import json
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):
    # TODO implement

    instance_list = []
    f_tag =  {'Name': 'tag:maintenance-automation', 'Values':['weekday']}

    ec2_response = ec2.describe_instances(Filters= [f_tag])['Reservations']
    for b in ec2_response:
        for c in b['Instances']:
            instance_list.append(c['InstanceId'])
    return {
        'statusCode': 200,
        'action': event['action'],
        'instances': instance_list
    }
