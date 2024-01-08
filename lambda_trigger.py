import json
import boto3
from pprint import pprint

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
        'body': json.dumps(event['action'])
    }
