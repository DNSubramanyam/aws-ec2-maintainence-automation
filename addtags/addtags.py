import boto3
import json
from pprint import pprint

instance_list = ['i-0ffe573476fedb1fe', 'i-070695bd0f30decc8']
asg_list = ['maintenance-asg-2']
tag_value = {"Env": "Dev", "Schedule": "weekend"}

f_tag = [{'Key': 'maintenance-automation', 'Value': json.dumps(tag_value)}]
asg_tag={'Key': 'maintenance-automation', 'Value': json.dumps(tag_value)}
ec2_resource = boto3.resource('ec2')
asg_client = boto3.client('autoscaling', region_name='us-east-1')

# for server in instance_list:
#     instance = ec2_resource.Instance(server)
#     response=instance.create_tags(Tags=f_tag)

for asg in asg_list:
    asg_tag2 = {'ResourceId': asg, 'ResourceType': 'auto-scaling-group', 'PropagateAtLaunch': True}
    response=asg_client.create_or_update_tags(Tags=[{**asg_tag, **asg_tag2}])
    pprint(response)

