import pytest
import json
from handler import handle_message_from_sqs_fifo


@pytest.fixture
def sqs_message_event (request):
    with open('tests/mockData/sqs_fifo_event.json') as f:
        return json.load(f)


def test_handle_message_from_sqs_fifo (sqs_message_event):
    res = handle_message_from_sqs_fifo(sqs_message_event, {})
    assert res['statusCode'] == 200
