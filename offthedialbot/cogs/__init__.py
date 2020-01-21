"""Dynamically import and generate discord.ext cogs."""
import importlib
import inspect
import os


def register_cogs(bot):
    """Register the cogs in the package."""
    modules = import_modules()
    cogs = get_cogs(modules)
    for cog in cogs:
        bot.add_cog(cog(bot))


def import_modules():
    """Imports all of the modules."""
    modules = []
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        modules.append(importlib.import_module(f"offthedialbot.cogs.{module[:-3]}"))
    del module

    return modules


def get_cogs(modules) -> list:
    """Imports the cogs from each module."""
    return [get_class(module) for module in modules]


def get_class(module):
    """Get the first class present in a given module."""
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            return obj
