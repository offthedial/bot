"""Contains function to create ClientSession."""

from offthedialbot import logger
import aiohttp


session = aiohttp.ClientSession()
logger.debug("New ClientSession has been created.")
