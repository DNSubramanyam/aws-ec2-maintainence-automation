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
    CmdId = "5c0378c6-3146-405f-9105-1324909e40f5"
    ins_list = ["i-03fedc8397cfeb632"]
    get_cmd_output(CmdId, ins_list)