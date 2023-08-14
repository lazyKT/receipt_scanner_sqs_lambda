import json
import logging
import boto3


def connection_manager (event, context):
    logging.debug(f"connection_manager::event::{event}")
    print(f"connection_manager::event::{event}")
    if event['requestContext']['eventType'] == "CONNECT":
        logging.info("Connection requested")
    elif event['requestContext']['eventType'] == 'DISCONNECT':
        logging.info("Disconect requested")
    else:
        logging.error("Connection manager received invalid evnet type!")
    return {
        "statusCode": 200,
    }

def default_handler (event, context):
    """
    : This function will be called if there's no handler to use for the ws event
    """
    logging.debug(f"default_handler::event::{event}")
    print(f"default_handler::event::{event}")
    return {
        "statusCode": 400,
        "body": f"No handler matched for the event"
    }


def send_message (event, context):
    print(f"Message sent on web-socker. {event}")
    endpoint_url = 'https://'+event['requestContext']['domainName']+'/'+ event['requestContext']['stage']
    apigateway = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=endpoint_url
    )
    apigateway.post_to_connection(
        ConnectionId=event['requestContext']['connectionId'],
        Data=json.dumps({'message': 'Reply from socket!'}).encode('utf-8')
    )
    body = json.loads(event.get("body", ""))
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
