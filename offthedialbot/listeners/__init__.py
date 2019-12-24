"""Dynamically import and generate discord.ext listeners."""
import os
import inspect
import importlib


def register_listeners(bot):
    """Registers listeners as part of the bot."""
    files = import_modules()
    listeners = get_listeners(files)
    for listener in listeners:
        setattr(bot, listener.__name__, derive_listener(listener, bot))


def import_modules():
    """Imports all of the modules."""
    modules = []
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        modules.append(importlib.import_module(f".{module[:-3]}", package="listeners"))
    del module

    return modules


def get_listeners(modules):
    """Imports the listener functions from each module."""
    return [get_function(module) for module in modules]


def get_function(module):
    """Get the first function present in a given module."""
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            return obj


def derive_listener(func, bot):
    """Derive listener from function."""
    async def _(*args, **kwargs):
        return await func(bot, *args, **kwargs)

    return _

