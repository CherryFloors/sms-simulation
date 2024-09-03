"""Test messages.py"""

from sms.messages import SMSMessage


class TestSMSMessage:
    """Test SMSMessage"""

    @staticmethod
    def test_random_message() -> None:
        """Test the random_message classmethod"""

        msg = SMSMessage.random_message()
        assert isinstance(msg.phone_number, str)
        assert len(msg.phone_number) == 10
        assert all(i.isdigit() for i in msg.phone_number)
        assert len(msg.message_body) <= 100

    @staticmethod
    def test_generator() -> None:
        """Test the generator class method"""

        gen = SMSMessage.generator(messages=4)

        messages = list(gen)
        assert len(messages) == 4
        for msg in messages:
            assert isinstance(msg.phone_number, str)
            assert len(msg.phone_number) == 10
            assert all(i.isdigit() for i in msg.phone_number)
            assert len(msg.message_body) <= 100
