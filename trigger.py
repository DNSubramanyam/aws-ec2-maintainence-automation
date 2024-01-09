import boto3
from pprint import pprint

f_tag =  {'Name': 'tag:maintenance-automation', 'Values':['weekday']}

con = boto3.session.Session()
ec2 = con.client('ec2', region_name='us-east-1')
ssm = con.client('ssm', region_name='us-east-1')
asg = con.client('autoscaling', region_name='us-east-1')
cw = boto3.client('cloudwatch', region_name='us-east-1')

instance_list = []
asg_list = []
alarm_list = []
instance_name = []
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

if len(instance_list) > 0:
    asg_response = asg.describe_auto_scaling_instances(InstanceIds = instance_list)['AutoScalingInstances']
    for a in asg_response:
        asg_list.append(a['AutoScalingGroupName'])
    asg_list = list(set(asg_list))
print(f'ASGs:{asg_list}\nInstances:{instance_list}')



# #Fetching all the alarms using the defined tag
# for e in range(len(instance_name)):
#     alarm_response = cw.describe_alarms(AlarmNamePrefix=instance_name[e]+ '-' + instance_list[e])['MetricAlarms']
#     for f in alarm_response:
#         alarm_list.append(f['AlarmName'])
