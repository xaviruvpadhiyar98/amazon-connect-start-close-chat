import json
import os
from contextlib import closing
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from websocket import create_connection

load_dotenv()


connect = boto3.client(
    "connect",
    region_name="eu-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)


InstanceId = "8c62f24b-95e0-47a2-953e-91a162366012"
contactFlowId = "2dd35d3c-8113-4183-ac5e-298f999fe7a3"
sessionAttributes = {}
ParticipantDetails = {"DisplayName": "Dhruv"}
InitialMessage = {"ContentType": "text/plain", "Content": "Hi"}
ClientToken = str(uuid4())
ChatDurationInMinutes = 60

start_chat_contact_response = connect.start_chat_contact(
    InstanceId=InstanceId,
    ContactFlowId=contactFlowId,
    Attributes=sessionAttributes,
    ParticipantDetails=ParticipantDetails,
    InitialMessage=InitialMessage,
    ClientToken=ClientToken,
    ChatDurationInMinutes=ChatDurationInMinutes,
)
print("start_chat_contact_response: ", end="")
print(json.dumps(start_chat_contact_response, indent=4))

with open("open_chat_contact_id.txt", "a", encoding="utf-8") as f:
    f.write(start_chat_contact_response["ContactId"] + "\n")


connectparticipant = boto3.client(
    "connectparticipant",
    region_name="eu-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)


create_participant_connection_response = (
    connectparticipant.create_participant_connection(
        Type=["WEBSOCKET", "CONNECTION_CREDENTIALS"],
        ParticipantToken=start_chat_contact_response["ParticipantToken"],
    )
)
print("create_participant_connection_response: ", end="")
print(json.dumps(create_participant_connection_response, indent=4))


send_message_response = connectparticipant.send_message(
    ConnectionToken=create_participant_connection_response["ConnectionCredentials"][
        "ConnectionToken"
    ],
    ContentType="text/plain",
    Content="Hi this is dhruv again.",
)
print("send_message_response: ", end="")
print(json.dumps(send_message_response, indent=4))

with closing(
    create_connection(
        create_participant_connection_response["Websocket"]["Url"], timeout=30
    )
) as conn:
    print(conn.send('{"topic":"aws/subscribe","content":{"topics":["aws/chat"]}}'))
    for _ in range(3):
        print(conn.recv())


get_transcript_response = connectparticipant.get_transcript(
    ConnectionToken=create_participant_connection_response["ConnectionCredentials"][
        "ConnectionToken"
    ],
    ContactId=start_chat_contact_response["ContactId"],
)
print("get_transcript_response: ", end="")
print(json.dumps(get_transcript_response, indent=4))


disconnect_participant_response = connectparticipant.disconnect_participant(
    ConnectionToken=create_participant_connection_response["ConnectionCredentials"][
        "ConnectionToken"
    ],
)
print("disconnect_participant_response: ", end="")
print(json.dumps(disconnect_participant_response, indent=4))

stop_contact_response = connect.stop_contact(
    InstanceId=InstanceId,
    ContactId=start_chat_contact_response["ContactId"],
)
print("stop_contact_response: ", end="")
print(json.dumps(stop_contact_response, indent=4))
