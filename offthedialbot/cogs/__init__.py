"""Dynamically import and generate discord.ext cogs."""
import importlib
import inspect
import os

from offthedialbot import logger


def register_cogs(bot):
    """Register the cogs in the package."""
    modules = import_modules()
    cogs = get_cogs(modules)
    for cog in cogs:
        bot.add_cog(cog(bot))


def import_modules():
    """Imports all of the modules."""
    modules = []
    for module in os.scandir(os.path.dirname(__file__)):
        if module.name == '__init__.py' or not module.name.endswith('.py'):
            continue
        modules.append(importlib.import_module(f"offthedialbot.cogs.{module.name[:-3]}"))
    del module

    return modules


def get_cogs(modules) -> list:
    """Imports the cogs from each module."""
    return [get_class(module) for module in modules if get_class(module)]


def get_class(module):
    """Get the first class present in a given module."""
    module_name = ".".join(module.__name__.split(".")[-1:])
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__name__ == ''.join([w.title() for w in module_name.split('_')]):
            return obj
    else:
        logger.warn(f"Cannot register cog in '{module_name}.py': Missing `{''.join([w.title() for w in module_name.split('_')])}`")
