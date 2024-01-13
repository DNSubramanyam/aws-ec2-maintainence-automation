import boto3
from pprint import pprint
from datetime import datetime

f_tag =  [{'Name': 'tag:maintenance-automation', 'Values':[{'Env': 'DV', 'Schedule': 'weekend'}]}]

con = boto3.session.Session()
ec2 = con.client('ec2', region_name='us-east-1')
ssm = con.client('ssm', region_name='us-east-1')
asg = con.client('autoscaling', region_name='us-east-1')
cw = con.client('cloudwatch', region_name='us-east-1')
dynamodb = con.resource('dynamodb', region_name='us-east-1')

instance_list = []
asg_list = []
alarm_list = []
instance_name = []
executiondetails = {}
action='stop'
table_name='test-table'

def initiate_phase1_execution(ins_id):
    exec_id=ssm.start_automation_execution(
        DocumentName='ec2-maintenance-stop',
        DocumentVersion='$DEFAULT',
        Parameters={
            'InstanceID': [ins_id],
            'SnsTopicARN': ['arn:aws:sns:us-east-1:366951018568:EC2-maintanance-automation']
        }
    )['AutomationExecutionId']
    return exec_id
dt = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

def write_to_table(db, table, to_write):
    db_table = db.Table(table)
    db_table.put_item(Item=to_write)

ec2_response = ec2.describe_instances(Filters= f_tag)['Reservations']
for b in ec2_response:
    for c in b['Instances']:
        instance_list.append(c['InstanceId'])

if len(instance_list) > 0:
    asg_response = asg.describe_auto_scaling_instances(InstanceIds = instance_list)['AutoScalingInstances']
    for a in asg_response:
        asg_list.append(a['AutoScalingGroupName'])
        to_write={
            'InstanceId': a['InstanceId'],
            'AutoScalingGroup': a['AutoScalingGroupName'],
            'Timestamp': datetime.now().strftime("%d-%m-%Y_%H:%M:%S"),
            'Environment': 'Dev',
            'action': action
        }
        write_to_table(db=dynamodb,table=table_name,to_write=to_write)
    asg_list = list(set(asg_list))
print(f'ASGs:{asg_list}\nInstances:{instance_list}')


# #Fetching all the alarms using the defined tag
# for e in range(len(instance_name)):
#     alarm_response = cw.describe_alarms(AlarmNamePrefix=instance_name[e]+ '-' + instance_list[e])['MetricAlarms']
#     for f in alarm_response:
#         alarm_list.append(f['AlarmName'])
