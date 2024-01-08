import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')

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

def lambda_handler(event, context):
    # TODO implement

    instance_list = []
    executiondetails = {}

    f_tag =  {'Name': 'tag:maintenance-automation', 'Values':['weekday']}

    ec2_response = ec2.describe_instances(Filters= [f_tag])['Reservations']
    for b in ec2_response:
        for c in b['Instances']:
            instance_list.append(c['InstanceId'])
            initiate_stop_execution(c['InstanceId'])
            executiondetails[c['InstanceId']]=''
            executiondetails[c['InstanceId']]=initiate_stop_execution(c['InstanceId'])
    return {
        'statusCode': 200,
        'action': event['action'],
        'instances': instance_list,
        'executionIds': executiondetails
    }
