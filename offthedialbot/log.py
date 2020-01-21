"""Set's up logging for the bot."""
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: [%(levelname)s] %(message)s',
    datefmt='%m-%d-%Y|%H-%M-%S'
)
logging.getLogger("discord").setLevel(logging.ERROR)

logger = logging.getLogger("__name__")
