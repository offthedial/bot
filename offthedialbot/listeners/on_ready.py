"""Contains on_ready listener."""

from collections import defaultdict

from offthedialbot import env


async def on_ready(client):
    """When the bot is ready."""
    set_vars(client)

    # Ready!
    client.logger.info(f'Logged in as: {client.user}')
    if env.get('debug'):
        client.logger.info(f'Running in debug mode. Do not use for production.')


def set_vars(client):
    """Set client variables."""
    client.OTD = client.get_guild(374715620052172800)
    client.ongoing_commands = defaultdict(set)
