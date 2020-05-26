"""Contains custom decorators."""
from functools import wraps
import inspect

from offthedialbot import env, utils


def profile_required(reverse=False, competing=False):
    """Make sure the command is only callable if the user has a profile."""

    if reverse:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    utils.Profile(get_ctx(_, args).author.id)
                except utils.Profile.NotFound:
                    await command(*args)
                else:
                    await utils.Alert(get_ctx(_, args), utils.Alert.Style.DANGER,
                        title="Command Failed",
                        description="Existing profile found. You can edit it using `$profile update`.")

            return _

    elif competing:
        def deco(command):
            @wraps(command)
            async def _(*args):
                profile = utils.ProfileMeta(get_ctx(_, args).author.id)
                if profile.get_reg():
                    await command(*args)
                else:
                    await utils.Alert(get_ctx(_, args), utils.Alert.Style.DANGER,
                        title="Command Failed",
                        description="You are not currently competing.")

            return _

    else:
        def deco(command):
            @wraps(command)
            async def _(*args):
                try:
                    utils.Profile(get_ctx(_, args).author.id)
                except utils.Profile.NotFound:
                    await utils.Alert(get_ctx(_, args), utils.Alert.Style.DANGER,
                        title="Command Failed",
                        description="No profile found. You can create one using `$profile create`.")
                else:
                    await command(*args)

            return _

    return deco


def otd_only(command):
    """Make sure the command is only called in Off the Dial."""

    @wraps(command)
    async def _(*args):
        ctx = get_ctx(_, args)
        if ctx.guild and ctx.bot.OTD and ctx.guild.id == ctx.bot.OTD.id:
            await command(*args)
        elif env.get('debug'):
            await command(*args)
        else:
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title="Command Failed",
                description="This command must be performed in Off the Dial.")

    return _


def require_role(role: str):
    """Make sure the command is only callable with role."""

    def deco(command):
        """Make sure the command is only callable by tournament organisers."""

        @wraps(command)
        async def _(*args):
            ctx = get_ctx(_, args)
            if ctx.guild and utils.roles.has(ctx.author, role):
                await command(*args)
            else:
                await utils.Alert(ctx, utils.Alert.Style.DANGER,
                    title="Permission Denied",
                    description=f"This command is only avaliable to {role}s.")

        return _

    return deco


def tourney(step: int = None):
    """ Require tournament to call command.

    :param int step: The step the tournament should be at when the command is run. If None, the tournament simply must exist.
    """
    error_msg = lambda ctx, d: utils.Alert(ctx, utils.Alert.Style.DANGER, title="Command Failed", description=d)

    if step is None:
        def deco(command):
            @wraps(command)
            async def _(*args):
                if utils.tourney.get():
                    await command(*args)
                else:
                    await error_msg(get_ctx(_, args), "Tournament does not exist.")

            return _

    else:
        def deco(command):
            @wraps(command)
            async def _(*args):
                current_step = utils.tourney.current_step()
                if step > current_step:
                    await error_msg(get_ctx(_, args), "The tournament isn't at the required step yet.")
                elif step < current_step:
                    await error_msg(get_ctx(_, args), "The tournament is already past the required step.")
                else:
                    await command(*args)

            return _

    return deco


def get_ctx(func, args):
    return args[list(inspect.signature(func).parameters).index('ctx')]
