"""Contains custom decorators."""
from offthedialbot import utils
from functools import wraps


def profile_required(reverse=False, competing=False):
    """Make sure the command is only callable if the user has a profile."""
    if reverse:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    utils.Profile(args[-1].author.id)
                except utils.Profile.NotFound:
                    await command(*args)
                else:
                    await utils.Alert(args[-1], utils.Alert.Style.DANGER, title="Command Failed", description="Existing profile found. You can edit it using `$profile update`.")
            return _
    elif competing:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    profile = utils.Profile(args[-1].author.id)
                except utils.Profile.NotFound:
                    profile = None
                if profile and profile.get_competing():
                    await command(*args)
                else:
                    await utils.Alert(args[-1], utils.Alert.Style.DANGER, title="Command Failed", description="You are not currently competing.")

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
    """Make sure the command is only called in Off the Dial."""
    @wraps(command)
    async def _(ctx):
        if ctx.guild and ctx.bot.OTD and ctx.guild.id == ctx.bot.OTD.id:
            await command(ctx)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Command Failed", description="This command must be performed in Off the Dial.")
    
    return _


def to_only(command):
    """Make sure the command is only callable by tournament organisers."""
    @wraps(command)
    async def _(ctx):
        if ctx.guild and "Organiser" in [role.name for role in ctx.author.roles]:
            await command(ctx)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Permission Denied", description="This command is only avaliable to Tournament Organisers.")
    _.hidden = True
    return _


def dev_only(command):
    """Make sure the command is only callable by developers."""
    @wraps(command)
    async def _(ctx):
        if ctx.guild and "Developer" in [role.name for role in ctx.author.roles]:
            await command(ctx)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Permission Denied", description="This command is only avaliable to Developers.")
    _.hidden = True
    return _


def tourney(open=(True, False)):
    """ Require tournament to call command.

    open: Union[tribool, Tuple(True, False)]
        (default): Tournament exists
        None: Tournament does not exist
        True: Tournament registration is open
        False: Tournament registration is closed
    """
    error_msg = lambda ctx, d="Tournament does not exist.": utils.Alert(ctx, utils.Alert.Style.DANGER, title="Command Failed", description=d)

    if open == (True, False):
        def deco(command):
            @wraps(command)
            async def _(*args):
                if utils.dbh.get_tourney():
                    await command(*args)
                else:
                    await error_msg(args[-1])
            return _

    elif open is None:
        def deco(command):
            @wraps(command)
            async def _(*args):
                if not utils.dbh.get_tourney():
                    await command(*args)
                else:
                    await error_msg(args[-1], "Tournament already exists.")
            return _

    elif open is True:
        def deco(command):
            @wraps(command)
            async def _(*args):
                if (tourney := utils.dbh.get_tourney()):
                    if tourney["reg"]:
                        await command(*args)
                    else:
                        await error_msg(args[-1], "Tournament registration is not open.")
                else:
                    await error_msg(args[-1])
            return _

    elif open is False:
        def deco(command):
            @wraps(command)
            async def _(*args):
                if (tourney := utils.dbh.get_tourney()):
                    if not tourney["reg"]:
                        await command(*args)
                    else:
                        await error_msg(args[-1], "Tournament registration is currently open.")
                else:
                    await error_msg(args[-1])
            return _

    return deco
