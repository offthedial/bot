"""$to"""

import discord

from offthedialbot import utils


class To(utils.Command, hidden=True):
    """ Special commands for tournament organisers!

    Shows a dashboard when run on it's own.
    """

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Special commands for tournament organisers, shows dashboard.
        
        - Dashboard shows all tournament status things
        """