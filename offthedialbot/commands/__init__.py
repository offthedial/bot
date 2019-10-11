import inspect
import pkgutil
import sys

from discord.ext import commands


def _find_commands(module=sys.modules[__name__]):
    """ Recursively traverse submodules in search of coroutines.

        Any coroutines found are returned as a list.
    """
    data = {}

    def _nested_get(mapping, key, *args):
        value = mapping[key]
        if not args:
            return value
        return _nested_get(value['subcommands'], *args)

    # Adjust the name of the current module for submodule compatibility
    path = module.__file__
    if path.endswith('/__init__.py'):
        path, _, _ = module.__file__.rpartition('/')
    # Iterate over all modules
    for loader, module_name, _ in pkgutil.walk_packages([path]):
        hierarchy = module_name.split('.')

        # Load the module
        sub_module = loader.find_module(module_name).load_module(module_name)

        sub_dict = {'func': None, 'subcommands': {}}

        # Get the current node in the tree
        if len(hierarchy) == 1:
            # print(f'Module found: "{module_name}"')  # TODO: Use debug log
            data[module_name] = sub_dict
        else:
            # Retrieve the direct parent
            # print(f'Sub-module found: "{module_name}"')  # TODO: Use debug log
            parent = _nested_get(data, *hierarchy[:-1])
            parent['subcommands'][hierarchy[-1]] = sub_dict

        # Iterate over its contents
        for item_name in dir(sub_module):
            obj = getattr(sub_module, item_name)
            if inspect.iscoroutinefunction(obj) and item_name == 'main':
                sub_dict['func'] = obj

    return data


def _process_commands(data, parent):
    for name, cmd_dict in data.items():

        async def func(ctx, *, content=None):
            await cmd_dict['func'](ctx, content)

        subcommands = cmd_dict['subcommands']

        # If no "main" function was provided, skip
        if not func:
            print(
                f"Cannot register command '{name}': Missing `main`"
            )  # TODO: Use warning log
            continue

        # If subcommands were found, create a command group
        if subcommands:
            cmd = commands.Group(func, name=name)
            # Re-run this function for all of the subcommands
            _process_commands(subcommands, cmd)

        # Otherwise, create a normal command
        else:
            cmd = commands.Command(func, name=name)

        parent.add_command(cmd)


def register_commands(bot):
    command_dict = _find_commands()
    _process_commands(command_dict, bot)
