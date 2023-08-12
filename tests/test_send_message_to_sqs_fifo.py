import json
import pathlib
import pytest
from handler import send_message_to_sqs_fifo


@pytest.fixture
def lambda_event (request):
    with open('tests/mockData/lambda_event.json') as f:
        return json.load(f)


def test_send_message_to_sqs_fifo (lambda_event):
    res = send_message_to_sqs_fifo(lambda_event, {})
    assert res['statusCode'] == 200

