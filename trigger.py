import boto3
from pprint import pprint

f_tag =  {'Name': 'tag:maintenance-automation', 'Values':['weekday']}

con = boto3.session.Session()
ec2 = con.client('ec2', region_name='us-east-1')
ssm = con.client('ssm', region_name='us-east-1')

instance_list = []
executiondetails = {}
action='stop'

def initiate_stop_execution(ins_id):
    exec_id=ssm.start_automation_execution(
        DocumentName='ec2-maintenance-stop',
        DocumentVersion='$DEFAULT',
        Parameters={
            'InstanceID': [ins_id],
            'SnsTopicARN': ['arn:aws:sns:us-east-1:366951018568:EC2-maintanance-automation']
        }
    )['AutomationExecutionId']
    return exec_id


ec2_response = ec2.describe_instances(Filters= [f_tag])['Reservations']
for b in ec2_response:
    for c in b['Instances']:
        instance_list.append(c['InstanceId'])
        initiate_stop_execution(c['InstanceId'])
        executiondetails[c['InstanceId']]=''
        executiondetails[c['InstanceId']]=initiate_stop_execution(c['InstanceId'])

pprint(executiondetails)

