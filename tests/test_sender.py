"""Test the sender.py module"""

import multiprocessing
from unittest.mock import patch

from pytest import fixture

from sms.sender import SMSSender
from sms.messages import SMSMessage, ServicedMessage


class MockQueue:
    def __init__(self) -> None:
        self.items = []  # type: ignore

    def put(self, obj) -> None:
        self.items.append(obj)


@fixture
@patch.object(multiprocessing, "Queue", new=MockQueue)
def sender() -> SMSSender:
    """Create SMSSenders with mock queues"""

    producer_queue: multiprocessing.Queue[SMSMessage] = multiprocessing.Queue()
    _result_queue: multiprocessing.Queue[ServicedMessage] = multiprocessing.Queue()

    return SMSSender(
        incoming_messages=producer_queue,
        serviced_messages=_result_queue,
        failure_rate=0.0,
        mean_send_time_seconds=1.0,
        sdev_send_time_seconds=0.25,
    )


@fixture
def message() -> SMSMessage:
    """SMS Message"""

    return SMSMessage(phone_number="1234567890", message_body="Test Message")


class TestSMSSender:
    """Test SMSSender"""

    @staticmethod
    def test_service_time(sender: SMSSender) -> None:
        """test process_message"""

        assert sender.failure_rate == 0.0
        assert sender.mean_send_time_seconds == 1.0
        assert sender.sdev_send_time_seconds == 0.25

        sender.mean_send_time_seconds = 0.1
        sender.sdev_send_time_seconds = 10

        service_time = sender._service_time()
        assert service_time >= 0

    @staticmethod
    def test_process_message_delivered(sender: SMSSender, message: SMSMessage) -> None:
        """test process_message"""

        assert sender.failure_rate == 0.0
        assert sender.mean_send_time_seconds == 1.0
        assert sender.sdev_send_time_seconds == 0.25

        processed_msg = sender.process_message(message)
        assert processed_msg.delivered
        assert processed_msg.service_time_seconds > 0.0
        assert processed_msg.message == message

    @staticmethod
    def test_process_message_fail(sender: SMSSender, message: SMSMessage) -> None:
        """test process_message"""

        assert sender.failure_rate == 0.0
        assert sender.mean_send_time_seconds == 1.0
        assert sender.sdev_send_time_seconds == 0.25

        sender.failure_rate = 1.0
        processed_msg = sender.process_message(message)
        assert not processed_msg.delivered
        assert processed_msg.service_time_seconds > 0.0
        assert processed_msg.message == message
