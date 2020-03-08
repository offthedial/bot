"""cogs.Timers"""
from discord.ext import tasks, commands
import discord

from offthedialbot import utils


class Timers(commands.Cog):
    """Contains timers cog."""
    def __init__(self, bot):
        self.bot = bot
        self.MAX_TIMERS = 5
        self.loop.start()

    @tasks.loop(seconds=2)
    async def loop(self):
        """Task loop that calls timers."""
        timers = utils.time.Timer.get()
        for timer in timers:
            if utils.time.datetime.utcnow() > timer["when"]:
                await self.call(timer)
                utils.dbh.timers.delete_one(timer)

    @commands.command(aliases=["reminders"])
    async def timers(self, ctx):
        """List reminders that the user owns."""
        timers = list(utils.time.Timer.get({"author": ctx.author.id}))
        options = {"create": "\U0001f6e0"}
        description = f"To create a new one, select {options['create']}."
        if timers:
            options.update({"edit": "\u270f", "delete": "\U0001f5d1"})
            description = description + f" To edit an existing one, select {options['edit']}, to delete an existing one, select {options['delete']}"
        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
            title="\u23f0 Timers",
            description=description
        ))
        ui.embed.add_field(
            name="Current timers:",
            value="\n".join([
                f"`{timer['when']}`: {timer['alert']['description']}"
                for timer in timers
            ]) if timers else "You currently don't have any ongoing timers."
        )
        reply = await ui.get_valid_reaction(list(options.values()))
        ui.embed.clear_fields()
        await {
            options["create"]: lambda: self.create(ui, timers),
            options.get("edit"): lambda: self.edit(ui, timers),
            options.get("delete"): lambda: self.delete(ui, timers),
        }[reply.emoji]()

        await ui.end(True)

    async def create(self, ui, timers):
        if len(timers) >= self.MAX_TIMERS:
            await utils.Alert(ui.ctx, utils.Alert.Style.DANGER, title="Maximum timers reached", description=f"You can't have more than `{self.MAX_TIMERS}` timers running at a time.")
            await ui.end(None)
        ui.embed.title = "New Timer."
        ui.embed.description = "When do you want to be reminded?"
        when, desc = await self.get_params(ui)
        utils.time.Timer.schedule(utils.time.User.parse(when), ui.ctx.author.id, ui.ctx.author.id, style=utils.Alert.Style.INFO, title="Time's up!", description=desc)
    
    async def edit(self, ui, timers):
        ui.embed.title = "Edit Timer."
        ui.embed.description = "React with the emoji corresponding to the timer you want to edit."
        timer = await self.choose_timer(ui, timers)
        when, desc = await self.get_params(ui)
        utils.dbh.timers.delete_one(timer)
        utils.time.Timer.schedule(utils.time.User.parse(when), ui.ctx.author.id, ui.ctx.author.id, style=utils.Alert.Style.INFO, title="Time's up!", description=desc)
    
    async def delete(self, ui, timers):
        ui.embed.title = "Delete Timer."
        ui.embed.description = "React with the emoji corresponding to the timer you want to delete."
        timer = await self.choose_timer(ui, timers)
        utils.dbh.timers.delete_one(timer)
    
    async def get_params(self, ui):
        ui.embed.description = "When do you want to be reminded?"
        when = await ui.get_valid_message(lambda m: utils.time.User.parse(m.content), {"title": "Invalid Time", "description": "That isn't a valid time."})
        ui.embed.description = "What do you want to be reminded about?"
        desc = await ui.get_reply()
        return when.content, desc.content
    
    async def choose_timer(self, ui, timers):
        if len(timers) == 1:
            return timers[0]
        ui.embed.add_field(
            name="Current timers:",
            value="\n".join([
                f"{emoji} `{timer['when']}`: {timer['alert']['description']}"
                for timer, emoji in zip(timers, utils.emojis.digits)
        ]))
        reply = await ui.get_valid_reaction(list(utils.emojis.digits[:len(timers)]))
        timer = timers[utils.emojis.digits.index(reply.emoji)]
        ui.embed.remove_field((len(ui.embed.fields)-1))
        return timer

    async def call(self, timer):
        destination = await self.get_destination(timer["destination"])
        await destination.send(embed=utils.Alert.create_embed(**timer["alert"]))

    async def get_destination(self, id):
        if not (dest := self.bot.get_channel(id)):
            if not (dest := self.bot.get_user(id)):
                raise TypeError("The id is not of channel or user.")
        return dest
