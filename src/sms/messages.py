"""messages"""

from __future__ import annotations
from collections.abc import Iterator
from random import randint, choices
import string


_CHARSET = string.ascii_letters + string.digits + " "


class SMSMessage:
    """
    Class representing an SMS Message

    Attributes
    ----------
    phone_number : `str`
        10 digit phone number
    message_body : `str`
        Message contents
    """

    phone_number: str
    message_body: str

    __slots__ = ("phone_number", "message_body")

    def __init__(self, phone_number: str, message_body: str) -> None:
        self.phone_number = phone_number
        self.message_body = message_body

    @classmethod
    def random_message(cls) -> SMSMessage:
        """
        Generate an SMS message to a random phone number with a body up to 100 chars

        Returns
        -------
        `SMSMessage`
        """

        return cls(
            phone_number="".join(choices(string.digits, k=10)),
            message_body="".join(choices(_CHARSET, k=randint(5, 100))),
        )

    @classmethod
    def generator(cls, messages: int = 1000) -> Iterator[SMSMessage]:
        """
        Creates a generator that produces random SMS messages

        Parameters
        ----------
        messages : `int = 1000`

        Returns
        -------
        `Iterator[SMSMessage]`
        """
        return (cls.random_message() for _ in range(messages))


class ServicedMessage:
    """
    An SMS message with service time and delivery status metadata
    """

    delivered: bool
    service_time_seconds: float
    message: SMSMessage

    __slots__ = ("delivered", "service_time_seconds", "message")

    def __init__(self, delivered: bool, service_time_seconds: float, message: SMSMessage) -> None:
        self.delivered = delivered
        self.service_time_seconds = service_time_seconds
        self.message = message
