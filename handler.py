import json
import re
import boto3
import logging
from utils import dynamodb_to_dict
from datetime import datetime


def send_message_to_sqs_fifo(event, context):
    from uuid import uuid1
    sqs = boto3.client('sqs')
    db = boto3.client('dynamodb')
    queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/937234528489/FIFOQueue.fifo'
    request_body = json.loads(event['body'])
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=request_body['image'],
        MessageGroupId='groupId',
        MessageDeduplicationId=str(uuid1())
    )
    db_res = db.put_item(
        TableName='queueStatusTable',
        Item={
            "messageId": {"S": response["MessageId"]},
            "status": {"S": "PROCESSING"},
            "data": {"S": ""}
        }
    )
    print("db_res", db_res)
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


def process_date(data: str):
    ddmmyyyy_pattern = r'\d\d[-|\s]\d\d[-|\s]\d\d\d\d'
    date_string = datetime.strftime(datetime.now(), '%d-%m-%y')
    for val in re.findall(ddmmyyyy_pattern, data):
        try:
            dd, mm, yyyy = [int(x) for x in re.split(r'[-|\s]', val)]
            datetime(year=yyyy, month=mm, day=dd)
            date_string = val
        except ValueError:
            pass
        else:
            return date_string
    return date_string

def process_total(lines: list):
    total_amount = 0.00
    for line in lines:
        if 'amount' in line.lower():
            ptn = r'\d+\.?\d+'
            match = re.search(ptn, line)
            if match is not None:
                total_amount = float(match.group())
                break
    return total_amount


def process(data: str) -> dict:
    lines = data.split('\n')
    receipt_date = process_date(data)
    return {
        "info": lines,
        "invoice_date": receipt_date,
        "total_amount": process_total(lines)
    }

def handle_message_from_sqs_fifo(event, context):
    import os
    from io import BytesIO
    from base64 import b64decode
    from PIL import Image
    import pytesseract

    if os.getenv('AWS_EXECUTION_ENV') is not None:
        os.environ['LD_LIBRARY_PATH'] = '/opt/lib'
        os.environ['TESSDATA_PREFIX'] = '/opt/tessdata'
    try:
        message_events = event['Records']
        processed_data = list()
        for message in message_events:
            db = boto3.client('dynamodb')
            try:
                image = BytesIO(b64decode(message['body']))
                res = db.get_item(
                    TableName='queueStatusTable',
                    Key={
                        'messageId': {'S': message['messageId']}
                    }
                )
                item = res['Item'] if res['Item'] is not None else None
                if item is not None and dynamodb_to_dict(item)['status'] == 'PROCESSING':
                    result = pytesseract.image_to_string(Image.open(image))
                    data = process(result)
                    db.put_item(
                        TableName='queueStatusTable',
                        Item={
                            "messageId": {"S": message["messageId"]},
                            "status": {"S": "DONE"},
                            "data": {"S": json.dumps(data)}
                        }
                    )
                    processed_data.append(data)
            except Exception as e:
                db.put_item(
                    TableName='queueStatusTable',
                    Item={
                        "messageId": {"S": message["messageId"]},
                        "status": {"S": "FAIL"},
                        "error": {"S": json.dumps(str(e)}
                    }
                )
                raise e
        print('processed_data', processed_data)
        return {"statusCode": 200, "body": json.dumps({"data": processed_data})}
    except Exception as e:
        logging.exception('[Error] handle_message_from_sqs_fifo')
        print('[Error] handle_message_from_sqs_fifo', str(e))



if __name__ == '__main__':
    with open('tests/mockData/sqs_fifo_event.json') as f:
        mock_event = f.read()
        res = handle_message_from_sqs_fifo (json.loads(mock_event), None)
        print('res', res)
