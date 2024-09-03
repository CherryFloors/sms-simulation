"""Test the producer module"""

import multiprocessing
from unittest.mock import patch

from sms.producer import SMSProducer
from sms.messages import SMSMessage


class MockQueue:
    items: list[SMSMessage]

    def __init__(self) -> None:
        self.items = []

    def put(self, obj: SMSMessage) -> None:
        self.items.append(obj)


class TestSMSProducer:
    """Test SMSProducer"""

    @staticmethod
    @patch.object(multiprocessing, "Queue", new=MockQueue)
    def test_fill_queue() -> None:
        """Test fill_queue"""

        _queue: multiprocessing.Queue[SMSMessage] = multiprocessing.Queue()
        producer = SMSProducer(messages=10, queue=_queue)
        producer.fill_queue()
        assert len(_queue.items) == 10  # type: ignore
