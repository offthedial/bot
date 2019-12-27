"""Contains code for $minesweeper."""
import random

import discord
import numpy as np

import utils


async def main(ctx):
    """$minesweeper command."""
    embed: discord.Embed = discord.Embed(color=0x1c2a32)
    embed.set_author(
        name="Minesweeper!", icon_url="https://emojipedia-us.s3.amazonaws.com/thumbs/120/twitter/131/bomb_1f4a3.png"
    )
    ui = await utils.CommandUI(ctx, embed)

    # Keys used by the for loop to hold the unique data per loop.
    keys = [
        {
            "type": "Size",
            "desc": "Enter a size `6` to `32`",
            "valid": lambda r: 6 <= int(r) <= 36,
            "out": None
        }, {
            "type": "Difficulty",
            "desc": "Enter a difficulty `1` to `10`, or `0` for a random difficulty.",
            "valid": lambda r: int(r) <= 10,
            "out": None
        }
    ]
    # Get size & difficulty
    for key in keys:
        embed.description = key["desc"]
        key["out"] = await ui.get_valid_message(
            valid=key["valid"], error_fields={
                "title": f"Invalid {key['type']}",
                "description": key["desc"]
            }
        )
    # Create minesweeper
    mines = Map(int(keys[0]["out"].content), int(keys[1]["out"].content))
    map_list = mines.create_mines()

    # Send minesweeper
    async with ctx.typing():
        [await ctx.send(message) for message in map_list]

    # Remove embed
    await ui.end(status=None)


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
