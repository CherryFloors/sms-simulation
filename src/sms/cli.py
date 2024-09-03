"""cli"""

from __future__ import annotations
import asyncio
import sys

import click

from sms import __version__
from sms.config import SimulationConfig
from sms.simulator import Simulator


@click.version_option(version=__version__)
@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--config", help="Path to config toml", type=str, required=False)
def run(config: str | None) -> None:
    """
    Run the simulation with the following settings:

        senders = 4
        messages = 1000
        failure_rate = 0.1
        mean_send_time = 0.1
        sdev_send_time = 0.025
        refresh = 0.5

    These can be configured through the use of a .toml file and the --config parameter
    """

    _config = SimulationConfig()
    if config is not None:
        _config = SimulationConfig.load_toml(toml=config)

    config_errors = _config.validate()
    if config_errors is not None:
        click.secho("CONFIG ERRORS:", bold=True)
        click.echo("\n".join([str(e.args) for e in config_errors]))
        sys.exit(1)

    click.echo("Starting simulation with the following settings:")
    click.echo(f"  messages = {_config.messages}")
    click.echo(f"  refresh  = {_config.refresh}")
    for sender in _config.senders:
        click.echo(f"  sender   = {sender}")

    simulation = Simulator.from_config(_config)
    asyncio.run(simulation.run())
    click.echo("Simulation Complete. Thanks for flying with us today.")
