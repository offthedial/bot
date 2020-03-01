from discord.ext import commands

from offthedialbot import utils


async def on_command_error(client, ctx, error):
    """When an error occurs."""
    if not any({
        await invalid_command(ctx, error),
        await command_cancel(ctx, error)
    }):
        raise error


async def invalid_command(ctx, error):
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.TooManyArguments)):
        if ctx.command:
            await ctx.send_help(ctx.command)
        else:
            await ctx.send_help()
        return True


async def command_cancel(ctx, error):
    if not getattr(error, 'original', False):
        return False
    elif isinstance(error.original, utils.exc.CommandCancel):
        return True