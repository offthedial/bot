"""Contains on_command_error listener."""

from discord.ext import commands

from offthedialbot import utils


async def on_command_error(client, ctx, error):
    """When an error occurs."""
    if not any({
        await invalid_command(ctx, error),
        await disabled_command(ctx, error),
        await command_cancel(ctx, error)
    }):
        raise error


async def invalid_command(ctx, error):
    """Command is invalid."""
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.TooManyArguments)):
        if ctx.command:
            await ctx.send_help(ctx.command)
        else:
            await ctx.send_help()
        return True


async def disabled_command(ctx, error):
    """Command is disabled."""
    if isinstance(error, commands.errors.DisabledCommand):
        await utils.Alert(ctx, utils.Alert.Style.DANGER,
            title="Command Disabled",
            description="You can't use this command right now.")
        return True


async def command_cancel(ctx, error):
    """CommandCancel is raised."""
    if getattr(error, 'original', False) is False:
        return False
    if isinstance(error.original, utils.exc.CommandCancel):
        return True
