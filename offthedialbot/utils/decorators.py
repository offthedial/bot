"""Contains custom decorators."""
from offthedialbot import utils
from functools import wraps


def profile_required(reverse=False):
    """Makes sure the command is only callable if the user has a profile."""
    if not reverse:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    utils.Profile(args[-1].author.id)
                except utils.Profile.NotFound:
                    await utils.Alert(args[-1], utils.Alert.Style.DANGER, title="Command Failed", description="No profile found. You can create one using `$profile create`.")
                else:
                    await command(args[-1])
            return _
    else:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    utils.Profile(args[-1].author.id)
                except utils.Profile.NotFound:
                    await command(args[-1])
                else:
                    await utils.Alert(args[-1], utils.Alert.Style.DANGER, title="Command Failed", description="Existing profile found. You can edit it using `$profile update`.")
            return _
    return deco


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
