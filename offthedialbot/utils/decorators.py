"""Contains custom decorators."""
from offthedialbot import utils
from functools import wraps


def otd_only(command):
    """Makes sure the command is only called in Off the Dial."""
    @wraps(command)
    async def _(ctx):
        if ctx.guild and ctx.bot.OTD and ctx.guild.id == ctx.bot.OTD.id:
            await command(ctx)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Command Failed", description="This command must be performed in Off the Dial.")
    
    return _


def to_only(command):
    """Makes sure the command is only callable by tournament organisers."""
    @wraps(command)
    async def _(ctx):
        if (role := utils.roles.organizer(ctx.bot)) and role in ctx.author.roles:
            await command(ctx)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Permission Denied", description="This command is only avaliable to Tournament Organisers.")
    
    return _
