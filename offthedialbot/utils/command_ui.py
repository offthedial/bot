"""Holds api for working with a custom command ui."""
import utils
import asyncio


class CommandUI:

    async def __new__(cls, ctx, embed):
        """Create command embed with async on class creation."""
        self = super().__new__(cls)

        self.ctx = ctx
        self.embed = embed
        self.ui, self.cancel_task = await self.create_ui()

        return self

    async def create_ui(self):
        """Create and return the discord embed UI."""
        ui = await self.ctx.send(embed=self.embed)
        await ui.add_reaction('❌')

        task = await asyncio.create_task(self.wait_cancel_task())
        return ui, task

    async def wait_cancel_task(self):
        """Passively wait for the user to cancel the command."""
        reply, _ = await self.ctx.bot.wait_for(
            'reaction_add',
            check=lambda r: utils.checks.react(r, self.ctx),
        )
        await self.end(status=False)

    async def update(self):
        """Update the ui with new information."""
        await self.ui.edit(embed=self.embed)

    async def end(self, status: bool):
        """End UI interaction and display status."""
        key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED}
        self.cancel_task.cancel()
        await self.ui.edit(embed=key[status])
        await self.ui.clear_reactions()

    async def get_reply(self, event: str = 'message', *, timeout: int = 120, valids: list = None):
        """Get the reply from the user."""
        for react in (valids if valids else []):
            await self.ui.add_reaction(react)

        check = {
            'message': lambda m: utils.checks.msg(m, self.ctx),
            'reaction_add': lambda r: utils.checks.react(r, self.ctx, valids=valids)
        }
        try:
            reply = await self.ctx.bot.wait_for(
                event,
                check=check[event],
                timeout=timeout,
            )
            await reply.delete()

        except asyncio.TimeoutError:
            await self.end(status=False)
            reply = None

        return reply
