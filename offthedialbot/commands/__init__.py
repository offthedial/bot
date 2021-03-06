"""Dynamically import and generate discord.ext commands."""

from functools import wraps
import inspect
import pkgutil
import sys

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
        sub_dict = {'class': None, 'subcommands': {}}

        # Get the current node in the tree
        if len(hierarchy) == 1:
            data[module_name] = sub_dict
        else:
            # Retrieve the direct parent
            parent = recursive_get(data, *hierarchy[:-1])
            parent['subcommands'][hierarchy[-1]] = sub_dict

        # Iterate over its contents
        for cmd_name in dir(sub_module):
            attr = getattr(sub_module, cmd_name)
            if inspect.isclass(attr) and attr.__name__ == ''.join([w.title() for w in module_name.split('.')]):
                sub_dict['class'] = attr
                break

    return data


def process_commands(data, parent):
    """Extract main function and convert into an ext command."""
    for name, cmd_dict in data.items():

        command = derive_command(cmd_dict['class'], name)
        command_attrs = getattr(cmd_dict['class'], 'command_attrs', {})
        subcommands = cmd_dict['subcommands']

        # If subcommands were found, create a command group
        if subcommands:
            cmd = commands.Group(command, name=name, invoke_without_command=True, ignore_extra=False, **command_attrs)
            # Re-run this function for all of the subcommands
            process_commands(subcommands, cmd)

        # Otherwise, create a normal command
        else:
            cmd = commands.Command(command, name=name, ignore_extra=False, **command_attrs)

        parent.add_command(cmd)


def derive_command(command, name):
    """Wrap command in another function to parse arguments and exceptions."""
    warn = None
    if not command:
        warn = "class"
    elif not getattr(command, 'main', False):
        warn = f"'main' inside {command.__name__}"

    if warn:
        logger.warning("Cannot register command in '%s.py': Missing %s", name, warn)

        async def _(ctx):
            pass
    else:
        _ = command.main

    return _
