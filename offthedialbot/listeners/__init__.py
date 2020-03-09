"""Dynamically import and generate discord.ext listeners."""
import importlib
import inspect
from functools import wraps
import os

from offthedialbot import logger


def register_listeners(bot):
    """Registers listeners as part of the bot."""
    files = import_modules()
    listeners = get_listeners(files)
    for listener in listeners:
        setattr(bot, listener.__name__, derive_listener(listener, bot))


def import_modules():
    """Imports all of the modules."""
    modules = []
    for module in os.scandir(os.path.dirname(__file__)):
        if module.name == '__init__.py' or not module.name.endswith('.py'):
            continue
        modules.append(importlib.import_module(f"offthedialbot.listeners.{module.name[:-3]}"))
    del module

    return modules


def get_listeners(modules: list) -> list:
    """Imports the listener functions from each module."""
    return [get_function(module) for module in modules if get_function(module)]


def get_function(module):
    """Get the first function present in a given module."""
    for name, obj in inspect.getmembers(module):
        module_name = ".".join(module.__name__.split(".")[-1:])
        if inspect.isfunction(obj) and obj.__name__ == module_name:
            return obj
    else:
        logger.warn(f"Cannot register listener in '{module_name}.py': Missing `{module_name}`")


def derive_listener(func, bot):
    """Derive listener from function."""

    @wraps(func)
    async def _(*args, **kwargs):
        return await func(bot, *args, **kwargs)

    return _
