"""simulator"""

from __future__ import annotations
from datetime import datetime
from multiprocessing import Queue, Process
from textwrap import dedent
from dataclasses import dataclass
from queue import Empty
import asyncio
import os

import click

from sms.producer import SMSProducer
from sms.sender import SMSSender
from sms.config import SimulationConfig
from sms.messages import SMSMessage, ServicedMessage


_RESET_CURSOR = "\033[F"
if os.name == "nt":
    _RESET_CURSOR = "\x1b[A"


@dataclass
class SimulationStatistics:
    """
    Holds statistics and results of the simulation. The `new` method should be used to create new copy of the class.
    Attributes should not be changed manually, rather the values should be updated via the `update` method.

    Attributes
    ----------
    messages_sent : `int`
        Number of messages sent
    messages_failed : `int`
        Number of messages failed to send
    average_seconds_per_message : `float`
        Average send time per message
    start : `datetime`
        Start time of the simulation
    total_messages : `int`
        Total number of messages to be processed during the simlulation

    Methods
    -------
    new(total_messages: int) -> SimulationStatistics
        Factory method to build a new instance based on the total number of messages in the simulation
    update(self, serviced: ServicedMessage)
        Update the attributes based on the contents of a `ServicedMessage`
    render() -> str
        Provides a formatted string representing the current state of the simulation
    """

    messages_sent: int
    messages_failed: int
    average_seconds_per_message: float
    start: datetime
    total_messages: int

    @property
    def messages_processed(self) -> int:
        """
        The total number of processed messges (`messages_sent + messages_failed`)
        """

        return self.messages_sent + self.messages_failed

    @classmethod
    def new(cls, total_messages: int) -> SimulationStatistics:
        """
        Factory method to build a new instance based on the total number of messages in the simulation

        Parameters
        ----------
        total_messages : `int`
            The total number of messages that will be sent in the simulation

        Returns
        -------
        `SimulationStatistics`
        """

        return cls(
            messages_sent=0,
            messages_failed=0,
            average_seconds_per_message=0.0,
            start=datetime.now(),
            total_messages=total_messages,
        )

    def update(self, serviced: ServicedMessage) -> None:
        """
        Update the attributes based on the contents of a `ServicedMessage`. Update method counts time spent on failed
        messages towards the `average_seconds_per_message` calculation.

        Parameters
        ----------
        serviced : `ServicedMessage`
            A serviced message from the simulation
        """

        if serviced.delivered:
            self.messages_sent += 1
        else:
            self.messages_failed += 1

        self.average_seconds_per_message *= (self.messages_processed - 1) / self.messages_processed
        self.average_seconds_per_message += serviced.service_time_seconds / self.messages_processed

    def render(self) -> str:
        """
        Provides a formatted string representing the current state of the simulation

        Returns
        -------
        `str`
        """

        bar_width = 28
        space = " " * int(28 * ((self.total_messages - self.messages_processed) / self.total_messages))
        delivered = "=" * int((self.messages_sent / self.total_messages) * bar_width)
        failed = "-" * (bar_width - len(delivered) - len(space))

        avg = str(self.average_seconds_per_message)[:12]
        return dedent(
            f"""
            {click.style("SMS Simulator", bold=True)} [{datetime.now() - self.start}]

            Sent            {self.messages_sent}
            Failed          {self.messages_failed}
            Avg sec/message {avg}
            |{click.style(delivered, fg='green')}{click.style(failed, fg='red')}{space}|
            """
        )


@dataclass
class Engine:
    """
    Manages the producer and sender processes

    Attributes
    ----------
    producer : `Process`
        A process targing `SMSProducer.fill_queue`
    senders : `list[Process]`
        A list of processes targeting `SMSSender.service_queue`

    Methods
    -------
    new(producer: SMSProducer, senders: list[SMSSender]) -> Engine:
        Factory method to build a new instance from the producer and senders.
    start()
        Calls the `start` method on all processes to start the simulation
    kill()
        Calls the `kill` method on all processes to end the simulation
    """

    producer: Process
    senders: list[Process]

    @classmethod
    def new(cls, producer: SMSProducer, senders: list[SMSSender]) -> Engine:
        """
        Factory method to build a new instance from the producer and senders.

        Parameters
        ----------
        producer : `SMSProducer`
        senders : `list[SMSSender]`

        Returns
        -------
        `Engine`
        """

        return cls(
            producer=Process(target=producer.fill_queue, name="producer", daemon=True),
            senders=[Process(target=s.service_queue, name=f"sender_{i}", daemon=True) for i, s in enumerate(senders)],
        )

    def start(self) -> None:
        """Calls the `start` method on all processes to start the simulation"""

        for sender in self.senders:
            sender.start()

        self.producer.start()

    def kill(self) -> None:
        """Calls the `kill` method on all processes to end the simulation"""

        for sender in self.senders:
            sender.kill()

        self.producer.kill()


@dataclass
class Simulator:
    """
    Used to perform SMS simulations. For convenience, new instances of the class should be created vie the `from_config`
    factory method.

    Attributes
    ----------
    producer : `SMSProducer`
        An `SMSProducer` used in the simulation
    senders : `list[SMSSender]`
        A list of `SMSSender`'s used in the simulation
    result_queue : `Queue[ServicedMessage]`
        A multiprocessing queue to communicate results
    stats : `SimulationStatistics`
        Statistics about the current simulation
    running : `bool`
        Flag to signal that the simulation is running
    refresh : `float`
        Refresh rate from the progress
    engine : `Engine`
        The engine managing the processes

    Methods
    -------
    from_config(config: SimulationConfig) -> Simulator
        Factory method to build a new instance from a `SimulationConfig`.
    run()
        Async method that starts the simulation
    """

    producer: SMSProducer
    senders: list[SMSSender]
    result_queue: Queue[ServicedMessage]
    stats: SimulationStatistics
    running: bool
    refresh: float
    engine: Engine

    @classmethod
    def from_config(cls, config: SimulationConfig) -> Simulator:
        """
        Factory method to build a new instance from a `SimulationConfig`.

        Parameters
        ----------
        config : `SimulationConfig`

        Returns
        -------
        `Simulator`
        """

        max_q_size = 2 * len(config.senders)
        producer_queue: Queue[SMSMessage] = Queue(maxsize=max_q_size)
        _result_queue: Queue[ServicedMessage] = Queue(maxsize=max_q_size)

        _senders: list[SMSSender] = []
        for sender_config in config.senders:
            _sender = SMSSender(
                incoming_messages=producer_queue,
                serviced_messages=_result_queue,
                failure_rate=sender_config.failure_rate,
                mean_send_time_seconds=sender_config.mean_send_time,
                sdev_send_time_seconds=sender_config.sdev_send_time,
            )
            _senders.append(_sender)

        _producer = SMSProducer(messages=config.messages, queue=producer_queue)
        _engine = Engine.new(producer=_producer, senders=_senders)

        return cls(
            producer=_producer,
            senders=_senders,
            result_queue=_result_queue,
            stats=SimulationStatistics.new(total_messages=config.messages),
            running=False,
            refresh=config.refresh,
            engine=_engine,
        )

    async def _progress_monitor(self) -> None:
        """
        Async method to updated the progress monitor. Meant to run as an asyncio.task. Ending the task should be
        signaled by setting `Simulator.running` attribute to `False`
        """
        clear = _RESET_CURSOR * 8 + (" " * 30 + "\n") * 8 + _RESET_CURSOR * 9
        click.echo(self.stats.render())
        while self.running:
            click.echo(clear)
            click.echo(self.stats.render())
            await asyncio.sleep(self.refresh)

        click.echo(clear)
        click.echo(self.stats.render())

    async def run(self) -> None:
        """Async method that starts the simulation."""

        event_loop = asyncio.get_event_loop()
        progress_monitor_task = asyncio.create_task(self._progress_monitor())

        self.running = True
        self.engine.start()
        while self.running:
            try:
                msg = await event_loop.run_in_executor(None, self.result_queue.get, True, 0.5)
                await event_loop.run_in_executor(None, self.stats.update, msg)
            except Empty:
                pass

            if self.stats.messages_processed == self.producer.messages:
                self.running = False

        self.engine.kill()
        await progress_monitor_task
