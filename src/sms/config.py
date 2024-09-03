from __future__ import annotations
from dataclasses import dataclass
import os

import tomli


@dataclass
class SimulationConfig:
    """
    Configuration object for the SMS Simulation

    Attributes
    ----------
    senders : `int = 4`
        Total number of senders
    messages : `int = 1000`
        Total messages to send
    failure_rate : `float = 0.1`
        Fraction of messages that fail (should be between 0 and 1)
    mean_send_time : `float = 0.1`
        Average send time in seconds
    sdev_send_time : `float = 0.025`
        Standard deviation of the send time in seconds
    refresh : `float = 0.5`
        Progress monitor refresh rate
    """

    senders: int = 4
    messages: int = 1000
    failure_rate: float = 0.1
    mean_send_time: float = 0.1
    sdev_send_time: float = 0.025
    refresh: float = 0.5

    @classmethod
    def load_toml(cls, toml: str) -> SimulationConfig:
        """
        Load config from a toml file

        Parameters
        ----------
        toml : `str`
            Path to the toml file
        """
        with open(toml, "rb") as f:
            _toml = tomli.load(f)

        return SimulationConfig(**_toml["sms-simulation"])

    def validate(self) -> None | list[ValueError]:
        """
        Validate the configuration settings. Valid configurations return `None`. A list of `ValueError`'s will be
        returned if invalid settings are present

        Returns
        -------
        `None | list[ValueError]`
        """

        errors: list[ValueError] = []
        _cpu_count = os.cpu_count()
        if _cpu_count is None:
            _cpu_count = 3

        max_senders = _cpu_count - 2
        if self.senders > max_senders:
            errors.append(ValueError(f"Max senders for this platform = {max_senders}"))

        if self.messages < 0:
            errors.append(ValueError("messages should be positive"))

        if self.failure_rate < 0 or self.failure_rate > 1:
            errors.append(ValueError("failure_rate should be between 0 and 1"))

        if self.mean_send_time < 0:
            errors.append(ValueError("mean_send_time should be positive"))

        if self.sdev_send_time < 0:
            errors.append(ValueError("sdev_send_time should be positive"))

        if self.refresh < 0:
            errors.append(ValueError("refresh should be positive"))

        if len(errors) > 0:
            return errors

        return None
