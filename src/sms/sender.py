"""sender"""

from __future__ import annotations
from multiprocessing import Queue
from time import sleep
import random

from sms.messages import SMSMessage, ServicedMessage


class SMSSender:
    """
    A class used to simulate sending an SMS message

    Attributes
    ----------
    incoming_messages : `Queue[SMSMessage]`
    serviced_messages : `Queue[ServicedMessage]`
    failure_rate : `float`
    mean_send_time_seconds : `float`
    sdev_send_time_seconds : `float`

    Methods
    -------
    process_message(message: SMSMessage) -> ServicedMessage
       Simulate sending an SMS message
    service_queue()
        Service the producer queue
    """

    incoming_messages: Queue[SMSMessage]
    serviced_messages: Queue[ServicedMessage]
    failure_rate: float
    mean_send_time_seconds: float
    sdev_send_time_seconds: float

    def __init__(
        self,
        incoming_messages: Queue[SMSMessage],
        serviced_messages: Queue[ServicedMessage],
        failure_rate: float,
        mean_send_time_seconds: float,
        sdev_send_time_seconds: float,
    ) -> None:
        self.incoming_messages = incoming_messages
        self.serviced_messages = serviced_messages
        self.failure_rate = failure_rate
        self.mean_send_time_seconds = mean_send_time_seconds
        self.sdev_send_time_seconds = sdev_send_time_seconds

    def _service_time(self) -> float:
        """
        Generate a random service time. Service time is based on a normal distribution defined by the configured average
        and standard deviation. An upper and lower bound for the time is set to 3 standard deviation above and below the
        average. A hard lower limit is placed at zero if 3 standard deviations below is negative.

        Returns
        -------
        `float`
        """

        upper_bound = self.mean_send_time_seconds + 3 * self.sdev_send_time_seconds
        lower_bound = self.mean_send_time_seconds - 3 * self.sdev_send_time_seconds
        lower_bound = max(lower_bound, 0.0)

        service_time = random.gauss(mu=self.mean_send_time_seconds, sigma=self.sdev_send_time_seconds)
        if service_time < lower_bound:
            service_time = lower_bound

        if service_time > upper_bound:
            service_time = upper_bound

        return service_time

    def process_message(self, message: SMSMessage) -> ServicedMessage:
        """
        Simulate sending an SMS message. Will block for a random processing time to provide a real time simulation.
        Message failure is determined using random number generation and the failure rate.

        Parameters
        ----------
        message : `SMSMessage`
            An sms message to process

        Returns
        -------
        `ServicedMessage`
            A serviced SMS message with a processing time and delivery status.
        """

        _service_time = self._service_time()
        sleep(_service_time)

        _delivered = True
        if random.random() < self.failure_rate:
            _delivered = False

        return ServicedMessage(
            delivered=_delivered,
            service_time_seconds=_service_time,
            message=message,
        )

    def service_queue(self) -> None:
        """
        Process messages from the producer queue and relay the processed messages back via the serviced message queues.
        Method will block at both queues if they are full or empty.
        """

        while True:
            msg = self.incoming_messages.get()
            processed_msg = self.process_message(message=msg)
            self.serviced_messages.put(processed_msg)
