"""Set up logging for the bot."""
import logging

from offthedialbot import env


logging.basicConfig(
    level=logging.DEBUG if env.get("debug") else logging.INFO,
    format='%(asctime)s: [%(levelname)s] %(message)s',
    datefmt='%m-%d-%Y|%H-%M-%S'
)
logging.getLogger("discord").setLevel(logging.ERROR)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logger = logging.getLogger("__name__")
