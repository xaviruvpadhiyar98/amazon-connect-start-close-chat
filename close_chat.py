import json
import os

import boto3
from dotenv import load_dotenv

load_dotenv()


with open("open_chat_contact_id.txt", "r", encoding="utf-8") as f:
    contactIds = f.read().split("\n")


connect = boto3.client(
    "connect",
    region_name="eu-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)

for contactId in contactIds:
    if not contactId:
        continue
    print(f"ContactId: {contactId}")
    stop_contact_response = connect.stop_contact(
        InstanceId="8c62f24b-95e0-47a2-953e-91a162366012",
        ContactId=contactId,
    )
    print(json.dumps(stop_contact_response, indent=4))


with open("open_chat_contact_id.txt", "w", encoding="utf-8") as f:
    f.write("")
