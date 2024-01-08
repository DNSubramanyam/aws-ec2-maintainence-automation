import boto3
from pprint import pprint

f_tag =  {'Name': 'tag:maintenance-automation', 'Values':['weekday']}

con = boto3.session.Session()
ec2 = con.client('ec2', region_name='us-east-1')

instance_list = []
action='stop'

ec2_response = ec2.describe_instances(Filters= [f_tag])['Reservations']
for b in ec2_response:
    for c in b['Instances']:
        instance_list.append(c['InstanceId'])

pprint(f'Instance list: {instance_list}' )

