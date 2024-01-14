import boto3
from pprint import pprint

def get_cmd_output(cid, ins):
    ssm = boto3.client('ssm', region_name='us-east-1')
    for m in ins:
        response = ssm.get_command_invocation(CommandId=cid, InstanceId=m)
        if response['Status'] == "Success":
            print(f'{m} --> Yes --> {response["StandardOutputContent"]}')
        else:
            print(f'{m} --> No --> None ')


if __name__ == "__main__":
    CmdId = "0733c8fb-51e3-4bd9-9ff5-2b5012e5a1b5"
    ins_list = ["i-06062a3ab33387326","i-005bc05b354361bab"]
    get_cmd_output(CmdId, ins_list)