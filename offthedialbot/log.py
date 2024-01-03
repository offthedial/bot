"""Set up logging for the bot."""

import logging

from offthedialbot import env

logging.basicConfig(
    level=logging.DEBUG if env.get("debug") else logging.INFO,
)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logger = logging.getLogger("__name__")

if not env.get('token'):
    logger.warning("Cannot find 'token' key in config.yml")
if not env.get('smashgg'):
    logger.warning("Cannot find 'smashgg' key in config.yml")
