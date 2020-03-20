"""Dynamically import and generate discord.ext commands."""
import inspect
import pkgutil
import sys
from functools import wraps

from discord.ext import commands

from offthedialbot import logger


def register_commands(bot):
    """Register the commands in the package."""
    command_dict = find_commands()
    process_commands(command_dict, bot)


def find_commands(module=sys.modules[__name__]):
    """Recursively traverse submodules in search of coroutines."""
    data = {}

    def recursive_get(mapping, key, *args):
        """Recursively get."""
        value = mapping[key]
        if not args:
            return value
        return recursive_get(value['subcommands'], *args)

    # Adjust the name of the current module for submodule compatibility
    path = module.__file__[:-12]

    # Iterate over all modules
    for loader, module_name, _ in pkgutil.walk_packages([path]):
        hierarchy = module_name.split('.')

        # Load the module
        sub_module = loader.find_module(module_name).load_module(module_name)
        sub_dict = {'func': None, 'subcommands': {}}

        # Get the current node in the tree
        if len(hierarchy) == 1:
            data[module_name] = sub_dict
        else:
            # Retrieve the direct parent
            parent = recursive_get(data, *hierarchy[:-1])
            parent['subcommands'][hierarchy[-1]] = sub_dict

        # Iterate over its contents
        for item_name in dir(sub_module):
            obj = getattr(sub_module, item_name)
            if inspect.iscoroutinefunction(obj) and item_name == 'main':
                sub_dict['func'] = obj

    return data


def process_commands(data, parent):
    """Extract main function and convert into an ext command."""
    for name, cmd_dict in data.items():

        func = derive_command(cmd_dict['func'], name)
        func.hidden = getattr(func, 'hidden', False)
        subcommands = cmd_dict['subcommands']

        # If subcommands were found, create a command group
        if subcommands:
            cmd = commands.Group(func, name=name, invoke_without_command=True, ignore_extra=False, hidden=func.hidden)
            # Re-run this function for all of the subcommands
            process_commands(subcommands, cmd)

        # Otherwise, create a normal command
        else:
            cmd = commands.Command(func, name=name, ignore_extra=False, hidden=func.hidden)

        parent.add_command(cmd)


def derive_command(func, name):
    """Wrap command in another function to parse arguments and exceptions."""
    if not func:
        logger.warn(f"Cannot register command '{name}': Missing `main`")

        async def func(ctx):
            pass

    @wraps(func)
    async def _(ctx):
        await func(ctx)

    return _
