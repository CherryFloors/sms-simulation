"""Test the simulator.py module"""

from pytest import fixture

from sms.messages import SMSMessage, ServicedMessage
from sms.simulator import SimulationStatistics


@fixture
def stats() -> SimulationStatistics:
    """SMS SimulationStatistics"""

    return SimulationStatistics.new(total_messages=3)


@fixture
def serviced_msg() -> ServicedMessage:
    """serviced SMS Message"""

    return ServicedMessage(
        delivered=True,
        service_time_seconds=3.0,
        message=SMSMessage(phone_number="1234567890", message_body="Test Message"),
    )


class TestSimulationStatistics:
    """Test SimulationStatistics"""

    @staticmethod
    def test_total_messages(stats: SimulationStatistics) -> None:
        """test total_messages"""

        assert stats.messages_sent == 0
        assert stats.messages_failed == 0
        assert stats.average_seconds_per_message == 0.0
        assert stats.total_messages == 3
        assert stats.messages_processed == 0

        stats.messages_sent = 1
        stats.messages_failed = 2
        assert stats.messages_processed == 3

    @staticmethod
    def test_update(stats: SimulationStatistics, serviced_msg: ServicedMessage) -> None:
        """test update"""

        assert stats.messages_sent == 0
        assert stats.messages_failed == 0
        assert stats.average_seconds_per_message == 0.0
        assert stats.total_messages == 3
        assert stats.messages_processed == 0

        stats.update(serviced=serviced_msg)
        assert stats.messages_sent == 1
        assert stats.messages_failed == 0
        assert stats.average_seconds_per_message == 3.0

        serviced_msg.delivered = False
        serviced_msg.service_time_seconds = 5.0
        stats.update(serviced=serviced_msg)

        assert stats.messages_sent == 1
        assert stats.messages_failed == 1
        assert stats.average_seconds_per_message == 4.0
