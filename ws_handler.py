import json
import logging
import boto3
from utils import dynamodb_to_dict


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


def check_queue_status (message_id: str):
    dynamodb = boto3.client('dynamodb')
    res = dynamodb.get_item(
        TableName='queueStatusTable',
        Key={
            'messageId': { 'S' : message_id }
        }
    )
    print(f'res, {res}')
    if res['Item'] is not None:
        return dynamodb_to_dict(res['Item'])
    else:
        raise RuntimeError(f'Queue item not found with message id, {message_id}')

def reply_to_client (connection_id: str, data: dict, event: any):
    endpoint_url = 'https://'+event['requestContext']['domainName']+'/'+ event['requestContext']['stage']
    print(f'[DEBUG] endpoint_url: {endpoint_url}')
    apigateway = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=endpoint_url
    )
    apigateway.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps({'message': data}).encode('utf-8')
    )


def send_message (event, context):
    print(f"Message sent on web-socker. {event}")
    connection_id = event['requestContext']['connectionId']
    message_id = json.loads(event.get('body'))['message']
    queue_status = check_queue_status(message_id)
    reply_to_client(connection_id, queue_status, event)
    body = json.loads(event.get("body", ""))
    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
