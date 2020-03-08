"""cogs.Misc"""
import random
import numpy as np

from discord.ext import tasks, commands
import discord

from offthedialbot import utils


class Misc(commands.Cog, name='misc'):
    """All of the miscellaneous commands."""
    def __init__(self, bot):
        self.bot = bot
        self.timer_loop.start()

    @commands.command(aliases=["mines"])
    async def minesweeper(self, ctx: commands.Context):
        """Generate minesweepers at your convenience."""

        class Map:
            """Class that holds the map of the minesweeper."""

            def __init__(self, size: int, difficulty: int):
                """Initilize the map."""
                self.size: int = size
                self.difficulty: int = random.randint(1, 10) if difficulty <= 0 else difficulty

                self.ALGORITHM = lambda: (np.cbrt(difficulty) * 0.8) * np.square(self.size) / 13

            def create_mines(self) -> list:
                """
                Wraps the creating of the minesweeper into a neat packaged class method.

                Returns:
                    A list of messages you paste seperately.
                """
                output: list = []

                board = self.set_bombs(self.create_map())
                text_board = self.convert_to_text(board)

                if len(text_board) >= 2000:
                    number_of_seperate_messages = np.ceil(len(text_board) / 2000)
                    splits = np.array_split(board, number_of_seperate_messages)
                    for split in splits:
                        text = self.convert_to_text(split)
                        if len(text) >= 2000:
                            for tex in text.splitlines():
                                output.append(tex)
                        else:
                            output.append(text)
                else:
                    output.append(text_board)

                return output

            def set_bombs(self, board):
                """Place the bombs in random places on the map."""
                bombs = Map._prob_round(self.ALGORITHM())
                placed = 0
                while placed < bombs:
                    x = random.randint(0, self.size - 1)
                    y = random.randint(0, self.size - 1)
                    if not board[x][y] >= 9:
                        board[x][y] = 9
                        self.set_numbers(x, y, board)
                        placed += 1
                return board

            def set_numbers(self, x, y, board):
                """Set the numbers around the bombs."""
                if x < self.size and y < self.size and board[x][y] >= 9:
                    for i in range(9):
                        try:
                            f = x - 1 + i % 3
                            h = y - 1 + int(i / 3)

                            if board[f, h] < 9 and abs(f) == f and abs(h) == h:
                                board[f, h] += 1
                        except IndexError:
                            pass

            def create_map(self):
                """Create the base map with zeros."""
                return np.zeros((self.size, self.size), dtype=int)

            @staticmethod
            def convert_to_text(board):
                """Convert the map array to text."""
                text_key = {
                    0: "||:white_large_square:|| ",
                    1: "||:one:|| ",
                    2: "||:two:|| ",
                    3: "||:three:|| ",
                    4: "||:four:|| ",
                    5: "||:five:|| ",
                    6: "||:six:|| ",
                    7: "||:seven:|| ",
                    8: "||:eight:|| ",
                    9: "||:bomb:|| ",
                }
                text_board = board.astype(object)
                for x in range(board.shape[0]):
                    for y in range(board.shape[1]):
                        text_board[x, y] = text_key[board[x, y]]
                text_board = "\n".join("".join(el for el in inner) for inner in text_board)
                return text_board

            @staticmethod
            def _prob_round(raw: float) -> int:
                dice = random.uniform(0, 1)
                try:
                    base = int(raw)
                    thresh = raw - base
                    if dice > thresh:
                        output = int(raw)
                    else:
                        output = int(raw) + 1
                    return output

                except ValueError:
                    print("Error! Value given is not a number!")

        embed: discord.Embed = discord.Embed(title="\U0001f4a3 Minesweeper!", color=0x1c2a32)
        ui = await utils.CommandUI(ctx, embed)

        # Keys used by the for loop to hold the unique data per loop.
        keys = [
            {
                "type": "Size",
                "desc": "Enter a size `6` to `32`",
                "valid": lambda m: 6 <= int(m.content) <= 36,
            }, {
                "type": "Difficulty",
                "desc": "Enter a difficulty `1` to `10`, or `0` for a random difficulty.",
                "valid": lambda m: int(m.content) <= 10,
            }
        ]
        values = []
        # Get size & difficulty
        for key in keys:
            embed.description = key["desc"]
            reply = await ui.get_valid_message(
                valid=key["valid"], error_fields={
                    "title": f"Invalid {key['type']}",
                    "description": key["desc"]
            })
            values.append(int(reply.content))
        # Create minesweeper
        mines = Map(*values)
        map_list = mines.create_mines()

        # Send minesweeper
        async with ctx.typing():
            [await ctx.send(message) for message in map_list]

        # Remove embed
        await ui.end(status=None)

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
        reply = await ui.get_reply('reaction_add', valid_reactions=list(options.values()))
        ui.embed.clear_fields()
        await {
            options["create"]: lambda: self.timer_create(ui, timers),
            options.get("edit"): lambda: self.timer_edit(ui, timers),
            options.get("delete"): lambda: self.timer_delete(ui, timers),
        }[reply.emoji]()

        await ui.end(True)

    async def timer_create(self, ui, timers):
        max_timers = 5
        if len(timers) >= max_timers:
            await utils.Alert(ui.ctx, utils.Alert.Style.DANGER, title="Maximum timers reached", description=f"You can't have more than `{max_timers}` timers running at a time.")
            await ui.end(None)
        ui.embed.title = "New Timer."
        ui.embed.description = "When do you want to be reminded?"
        when, desc = await self.timer_getparams(ui)
        utils.time.Timer.schedule(utils.time.User.parse(when), ui.ctx.author.id, ui.ctx.author.id, style=utils.Alert.Style.INFO, title="Time's up!", description=desc)
    
    async def timer_edit(self, ui, timers):
        ui.embed.title = "Edit Timer."
        ui.embed.description = "React with the emoji corresponding to the timer you want to edit."
        timer = await self.choose_timer(ui, timers)
        when, desc = await self.timer_getparams(ui)
        utils.dbh.timers.delete_one(timer)
        utils.time.Timer.schedule(utils.time.User.parse(when), ui.ctx.author.id, ui.ctx.author.id, style=utils.Alert.Style.INFO, title="Time's up!", description=desc)
    
    async def timer_delete(self, ui, timers):
        ui.embed.title = "Delete Timer."
        ui.embed.description = "React with the emoji corresponding to the timer you want to delete."
        timer = await self.choose_timer(ui, timers)
        utils.dbh.timers.delete_one(timer)
    
    async def timer_getparams(self, ui):
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
        reply = await ui.get_reply('reaction_add', valid_reactions=list(utils.emojis.digits[:len(timers)]))
        timer = timers[utils.emojis.digits.index(reply.emoji)]
        ui.embed.remove_field((len(ui.embed.fields)-1))
        return timer

    @tasks.loop(seconds=2)
    async def timer_loop(self):
        """Task loop that calls timers."""
        timers = utils.time.Timer.get()
        for timer in timers:
            if utils.time.datetime.utcnow() > timer["when"]:
                await self.timer_call(timer)
                utils.dbh.timers.delete_one(timer)

    async def timer_call(self, timer):
        destination = await self.timer_get_destination(timer["destination"])
        await destination.send(embed=utils.Alert.create_embed(**timer["alert"]))

    async def timer_get_destination(self, id):
        if not (dest := self.bot.get_channel(id)):
            if not (dest := self.bot.get_user(id)):
                raise TypeError("The id is not of channel or user.")
        return dest