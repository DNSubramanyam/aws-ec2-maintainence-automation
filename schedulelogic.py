from datetime import datetime
import json

def get_fetch_tag(action):
    current_day = datetime.now().weekday()
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

if __name__ == "__main__":
    print(len(get_fetch_tag('stop')))
