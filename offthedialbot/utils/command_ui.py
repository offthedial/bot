"""Holds api for working with a custom command ui."""
import utils
import asyncio


class CommandUI:

    def __init__(self, ctx, embed):
        """Initilize command UI and declare self variables."""
        self.ctx = ctx
        self.embed = embed
        self.reply_task = None

    async def __new__(cls, ctx, embed):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)

        await self.create_ui(ctx, embed)
        self.passive_task = await self.create_passive_task(ctx)

        return self

    @staticmethod
    async def create_ui(ctx, embed):
        """Create and return the discord embed UI."""
        ctx.ui = await ctx.send(embed=embed)
        await ctx.ui.add_reaction('❌')

    async def create_passive_task(self, ctx):
        task = asyncio.create_task(self.passive_wait(ctx))
        await task
        return task

    async def passive_wait(self, ctx):
        """Passively wait for the user to cancel the command."""
        reply, _ = await ctx.bot.wait_for(
            'reaction_add',
            check=lambda r, u: utils.checks.react((r, u), ctx, valids='❌'),
        )
        await self.end(status=False)

    async def update(self):
        """Update the ui with new information."""
        await self.ctx.ui.edit(embed=self.embed)

    async def end(self, status: bool):
        """End UI interaction and display status."""
        key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED}
        # self.cancel_task.cancel()
        # self.reply_task.cancel()
        await self.ctx.ui.edit(embed=key[status])
        await self.ctx.ui.clear_reactions()

    async def get_reply(self, event: str = 'message', *, timeout: int = 120, valids: list = None):
        """Get the reply from the user."""
        for react in (valids if valids else []):
            await self.ctx.ui.add_reaction(react)
        check = {
            'message': lambda m: utils.checks.msg(m, self.ctx),
            'reaction_add': lambda r, u: utils.checks.react((r, u), self.ctx, valids=valids)
        }
        self.reply_task = self.ctx.bot.wait_for(
            event,
            check=check[event],
            timeout=timeout,
        )
        try:
            reply = await self.reply_task
            await reply.delete()
        except asyncio.TimeoutError:
            await self.end(status=False)
            reply = None

        return reply
