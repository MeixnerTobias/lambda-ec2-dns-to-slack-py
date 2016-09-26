# AWS Lamdba function to be called from SNS notification on EC2 change status to be running and send public DNS to a Slack user
# Author: Tobias Meixner <>
# v1 - 26 September
import slacktoken
import json
import boto3
import logging
from slackclient import SlackClient

#init slack client with file included token
sc = SlackClient(slacktoken.token)

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.resource('ec2')

#run lambda main function
def lambda_handler(event, context):
    # Use the filter() method of the instances collection to retrieve instance referred in event payload from SNS
    #print("Received event: " + json.dumps(event, indent=2))

    #jsonfy the SNS message payload
    decodedmsg = json.loads(event['Records'][0]['Sns']['Message'])
    myinstaceid = decodedmsg['detail']['instance-id']
    filters = [
        {
            'Name': 'instance-id',
            'Values': [myinstaceid]
        }
    ]
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #loop found instances
    for myinstance in instances:
        #loop tags of instance
        for tag in myinstance.tags:
            #if current tag is Name
            if tag['Key'] == 'Name':
                #get slackuser from Name Tag of Instance
                slackuser = tag['Value'].replace('somecustomstring-', "@")

                # send message with public dns to slack user
                print sc.api_call(
                    "chat.postMessage", channel=slackuser, text=myinstance.public_dns_name,
                    username='Some user', icon_emoji=':aws:'
                )
