import boto3
from pprint import pprint
from time import sleep
import json
import logging
import sys
from datetime import datetime, date, timezone

# Connecting AWS console
asg = boto3.client('autoscaling', region_name='ap-south-1')
ec2 = boto3.client('ec2', region_name='ap-south-1')
cw = boto3.client('cloudwatch', region_name='ap-south-1')
sns = boto3.client('sns', region_name='ap-south-1')

# Defining waiter for ec2
start_waiter = ec2.get_waiter('instance_status_ok')

# Define and intialize logging
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

#SNS topic related stuff
sns_arn = 'arn:aws:sns:ap-south-1:366951018568:sample-testing-topic'
subject_success = "Successful || RASI-Cost-Optimization || Scheduled start notification"
subject_fail = "Failure || RASI-Cost-Optimization || Scheduled start notification"
subject_warning = "Warning || RASI-Cost-Optimization || Scheduled start notification"

#Defining ASG scaling processs
ScalingProcesses = ['Launch', 'Terminate', 'ReplaceUnhealthy', 'HealthCheck']

#Function for SNS notification 
def notify(msg, subject):
    today = date.today().strftime("%b-%d-%Y")
    sns.publish(TopicArn=sns_arn, Subject=subject+'_'+today, Message=msg)
    logger.info('Notification sent..!')

#Function for creating message body
def message_body(instance_name, asg_list):
    data1 = data2 = ''
    row1 = []
    status_respose = ec2.describe_instances(Filters = [{'Name': 'tag:Name', 'Values': instance_name}])['Reservations']
    for x in status_respose:
        for y in x['Instances']:
            for z in y['Tags']:           
                if z['Key'] == 'Name':
                    name = z['Value']
            state = y['State']['Name']
            if state == 'running':
                ip = y['PrivateIpAddress']
            elif state == 'terminated':
                state = y['State']['Name'] + ' ' + '[Skipped this instance]'
                ip = 'Null'
            else:
                state = y['State']['Name'] + ' ' + '[Skipped this instance]'
                ip = y['PrivateIpAddress']               
            row1.append((name + '\t:\t' + ip).ljust(30, ' ') + '\t==>\t' +  state.upper())
            name = ip = state = ''
    data1 = '\n'.join(row1) 
    a_r = asg.describe_auto_scaling_groups(AutoScalingGroupNames=asg_list)['AutoScalingGroups']
    row2 = []
    for u in a_r:
        group_name = u['AutoScalingGroupName']
        if len(u['SuspendedProcesses']) != 0:
            status = 'SUSPENDED'
        else:
            status = 'RESUMED'
        row2.append(group_name.ljust(40, ' ') + '\t==>\t' + status)
    data2 = '\n'.join(row2)
    if datetime.now().weekday() == 0:
        environment = 'DEV, UAT & QA'
    else:
        environment = 'DEV'
    message = f'\nExecution is successful..!\nAs today is {date.today().strftime("%A").lower()}, all {environment} servers are started at {datetime.now(timezone.utc).strftime("%H:%M %Z")}. \n\nServers actioned [Total = {len(instance_name)}] :\n\n{data1}\n\nASGs actioned [Total = {len(asg_list)}] : \n\n{data2}\n' 
    logger.info('Notification message created ..!')
    return message 

#Function to resume the ASGs
def resume_asg(asg_list):
    logger.info(f'Resuming processes for the {len(asg_list)} ASGs..!')
    try:
        for g in asg_list:
            asg.resume_processes(AutoScalingGroupName=g, ScalingProcesses=ScalingProcesses)
    except Exception as e:
        logger.error(f'Unable to resume ASGs, failing with error{e}')
        message = f'Unable to resume ASGs, failing with error:\n {e}\n\nAutoScalingGroups to be actioned:\n{asg_list}'
        notify(message, subject_fail)
        logger.info('Failure Notification sent ..!')
        sys.exit()
      
#Function to verify resume process of ASGs
def verify_resume(asg_list):
    suspended_list = []
    resume_details = {}
    logger.info('Verifying suspension process..!')
    response_verify = asg.describe_auto_scaling_groups(AutoScalingGroupNames=asg_list)['AutoScalingGroups']
    for h in response_verify:
        if len(h['SuspendedProcesses']) != 0:
            suspended_list.append(h['AutoScalingGroupName'])    
        else:
            resume_details.setdefault(h['AutoScalingGroupName'], [])
            resume_details[h['AutoScalingGroupName']] = h['SuspendedProcesses']
            continue
    if len(suspended_list) == 0:
        logger.info(f"All ASG's are resumed\n {resume_details}")
        return True
    else:
        logger.error(f"Resuming ASG's failed. Following ASG's are not resumed :\n {suspended_list}")
        message = f"Resuming ASG's failed. Following ASG's are not resumed :\n {suspended_list}"
        notify(message, subject_fail)
        logger.info('Failure Notification sent ..!')
        sys.exit()
    
#Fuction to enable alarms of EC2
def enable_alarms(alarm_list):
    if len(alarm_list) != 0:
        logger.info('Proceeding to enable alarm actions ..!')
        cw.enable_alarm_actions(AlarmNames=alarm_list)
    else:
        logger.info('No alarms to action..continuing ..!')
        return

#Fuction to verify alarm enabling process of EC2
def alarm_action_check(alarm_list):
    if len(alarm_list) != 0:
        temp_list = []
        response_alarm_actions = cw.describe_alarms(AlarmNames=alarm_list, AlarmTypes=['MetricAlarm'])['MetricAlarms']
        for i in response_alarm_actions:
            temp_list.append(str(i['ActionsEnabled'])) 
        if 'False' in temp_list:
            logger.error("alarm action enabling failed for few alarms..!")
            message = f'alarm action enabling failed for few alarms..!\n\n Alarms state: \n {temp_list}\nNote: Instances wll be started and ASGs will be resumed back'
            notify(message, subject_fail)
            logger.info('Warning Notification sent ..!')
            return True
        else:
            logger.info(f'All alarms are enabled..!\n {temp_list}')
            return True
    else:
        return True
    
#Function to start the EC2 instances
def start(instance_list):
    logger.info('Proceeding to start the instances..!')
    try:
        to_start = []
        for instanceid in instance_list:
            if instance_list[instanceid] == 'stopped':
                to_start.append(instanceid)
            else:
                logger.info(f'Skipping the start process for Instance {instanceid} as it is in {instance_list[instanceid]} state..!')
                continue
        ec2.start_instances(InstanceIds=to_start)
        start_waiter.wait(InstanceIds=to_start)
        logger.info('Instances are now started..!')
    except Exception as e:
        logger.error(f'Unable to start instances, failing with error --> {e}')
        message = f'Unable to start instances, failing with error --> {e}\n\n Actioned instances: {instance_list}'
        notify(message, subject_fail)
        logger.info('Failure Notification sent ..!')
        sys.exit()

#Lambda handler function
def lambda_handler(event, context):
    #Defining variables
    asg_list = []
    instance_list = {}
    instance_id = []
    instance_name = []
    alarm_list = []

#Defining correct tag to fetch from the current day
    current_day = datetime.now().weekday()
    if current_day == 0: 
        condition_tag = {'Name': 'tag:RASI-weekend-stop-start', 'Values': ['yes']}
        logger.info(f"As today is monday, all DEV, QA & PPE servers will be started ..!")
    elif current_day in [5, 6]:
        logger.info(f"Skipping the execution as today is {date.today().strftime('%A')} ..!")
        return {
        'statusCode': 200,
        'body': json.dumps('Skipping the execution as this is weekend ..!')
        }
    else:
        condition_tag = {'Name': 'tag:RASI-weekday-stop-start', 'Values': ['yes']}
        logger.info(f"As today is {date.today().strftime('%A')}, all DEV servers will be started ..!")

    if len(condition_tag)>0:
    #Fetching all the ASGs using the defined tag
        logger.info(f'Fetching the resources using condition tag {condition_tag}')

        asg_response = asg.describe_auto_scaling_groups(Filters = [condition_tag])['AutoScalingGroups']
        logger.info(f"Fetching all the ASGs as per the tag ..!")
        for a in asg_response:
            asg_list.append(a['AutoScalingGroupName'])
        logger.info(f"Fetched {len(asg_list)} ASGs as per the tag ..!\n{asg_list}")

    #Fetching all the EC2 instances using the defined tag
        ec2_response = ec2.describe_instances(Filters= [condition_tag])['Reservations']
        logger.info(f"Fetching all the Instances as per the tag ..!")
        for b in ec2_response:
            for c in b['Instances']:
                instance_list.setdefault(c['InstanceId'], '')
                instance_list[c['InstanceId']] = c['State']['Name']
                instance_id.append(c['InstanceId'])
                for d in c['Tags']:
                    if d['Key'] == 'Name':
                        instance_name.append(d['Value'])
        logger.info(f"Fetched {len(instance_list)} instances as per the tag ..!\n {instance_list}")

    #Fetching all the alarms using the defined tag
        logger.info(f"Fetching all the alarms as per the tag ..!")
        for e in range(len(instance_name)):
            alarm_response = cw.describe_alarms(AlarmNamePrefix=instance_name[e]+ '-' + instance_id[e])['MetricAlarms']
            for f in alarm_response:
                alarm_list.append(f['AlarmName'])
        logger.info(f"Fetched {len(alarm_list)} alarms as per the tag ..!\n {alarm_list}")

#Main Logic for start process
    if len(instance_list) > 0 and len(asg_list) > 0:
        start(instance_list)
        enable_alarms(alarm_list)
        sleep(6)
        if (alarm_action_check(alarm_list)):
            resume_asg(asg_list)
        if (verify_resume(asg_list)):
            logger.info('Script completed successfully ..!')
            notify(message_body(instance_name, asg_list), subject_success)
        return {
            'statusCode': 200,
            'body': json.dumps('Executed successfully !')
        }
    else:
        logger.info(f'No instances and ASGs are found with the applied condition tag {condition_tag}. Hence exiting the execution..!')
        warn_msg = f'No instances and ASGs are found with the applied condition tag {condition_tag}\nHence the execution is exited at {datetime.now(timezone.utc).strftime("%H:%M %Z")}.\nServers actioned : {len(instance_name)} \nASGs actioned : {len(asg_list)}'
        notify(warn_msg, subject_warning)
