import boto3
import json
from pprint import pprint
from datetime import datetime

def get_fetch_tag(action):
    #current_day = datetime.now().weekday()
    current_day = 4
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

def initiate_phase1_execution(ins_id):
    ssm = boto3.client('ssm', region_name='us-east-1')
    exec_id=ssm.start_automation_execution(
        DocumentName='ec2-maintenance-stop',
        DocumentVersion='$DEFAULT',
        Parameters={
            'InstanceID': [ins_id],
            'SnsTopicARN': ['arn:aws:sns:us-east-1:366951018568:EC2-maintanance-automation']
        }
    )['AutomationExecutionId']
    return exec_id

def lambda_handler(event, context):
    # TODO implement
    ec2 = boto3.client('ec2', region_name='us-east-1')
    asg = boto3.client('autoscaling', region_name='us-east-1')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    cw = boto3.client('cloudwatch', region_name='us-east-1')

    table_name=event['TableName']
    db_table = dynamodb.Table(table_name)
    
    instance_list = []
    instance_name = {}
    asg_list = []
    alarm_list = []

    filter = get_fetch_tag(event['action'])

    if len(filter) > 0:
        ec2_response = ec2.describe_instances(Filters=filter)['Reservations']
        for b in ec2_response:
            for c in b['Instances']:
                instance_list.append(c['InstanceId'])
                instance_name.setdefault(c['InstanceId'], '')
                for d in c['Tags']:
                    if d['Key'] == 'Name':
                        instance_name[c['InstanceId']] = d['Value']

        if len(instance_list) > 0:
            asg_response = asg.describe_auto_scaling_instances(InstanceIds = instance_list)['AutoScalingInstances']
            for a in asg_response:
                asg_list.append(a['AutoScalingGroupName'])
                to_write={
                    'InstanceId': a['InstanceId'],
                    'Timestamp': datetime.now().strftime("%d-%m-%Y_%H:%M:%S"),
                    'Name': instance_name[a['InstanceId']],
                    'AutoScalingGroup': a['AutoScalingGroupName']
                    
                }
                db_table.put_item(Item=to_write)
            asg_list = list(set(asg_list))

            for id, name in instance_name.items():
                alarm_response = cw.describe_alarms(AlarmNamePrefix=name+ '-' + id)['MetricAlarms']
                for f in alarm_response:
                    alarm_list.append(f['AlarmName'])

    return {
        'statusCode': 200,
        'action': event['action'],
        'InstanceID': instance_list,
        'ASG_list': asg_list,
        'Alarm_list': alarm_list
    }

if __name__ == "__main__":
    event = {'action': 'start', 'environment': 'Dev', 'TableName': 'maintenance-automation-table'}
    print(lambda_handler(event, None))