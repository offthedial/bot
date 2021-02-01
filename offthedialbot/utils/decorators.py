"""Contains custom decorators."""

import discord

from functools import wraps
import inspect

from offthedialbot import utils


def require_role(role: str):
    """Make sure the command is only callable with role."""

    def deco(command):
        """Make sure the command is only callable by tournament organisers."""

        @wraps(command)
        async def _(*args):
            ctx = get_ctx(_, args)
            if ctx.guild and discord.utils.get(ctx.author.roles, name=role):
                await command(*args)
            else:
                await utils.Alert(ctx, utils.Alert.Style.DANGER,
                    title="Permission Denied",
                    description=f"You do not have have the {role} role.")

        return _

    return deco


def get_ctx(func, args):
    return args[list(inspect.signature(func).parameters).index('ctx')]
