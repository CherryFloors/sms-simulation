"""producer"""

from __future__ import annotations
from multiprocessing import Queue

from sms.messages import SMSMessage


class SMSProducer:
    """
    A class used to fill a queue with SMS messages

    Attributes
    ----------
    messages : `int`
        Total number of messages to put in the queue
    queue : `Queue[SMSMessage]`
        A multiprocessing queue

    Methods
    -------
    fill_queue()
        Fill the queue with messages, will block unitil all messges are sent
    """

    messages: int
    queue: Queue[SMSMessage]

    def __init__(self, messages: int, queue: Queue[SMSMessage]) -> None:
        self.messages = messages
        self.queue = queue

    def fill_queue(self) -> None:
        """
        Fill the queue with messages. Blocks until all messages are sent and waits until there is space in the queue.
        """

        for msg in SMSMessage.generator(self.messages):
            self.queue.put(msg)
