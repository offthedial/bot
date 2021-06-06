"""$to names"""
import discord
from wonderwords import RandomWord

from offthedialbot import utils


class ToNames(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, arg):
        """Generate a bunch of team names."""
        r = RandomWord()
        try:
            arg = int(arg)
            await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
                title="Generated team names",
                description="\n".join([
                    f"`{cls.gen_team_name(r, letter)}`" for letter in cls.letters[:int(arg)]
                ]))
        except ValueError:
            await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
                title="Generated custom team name",
                description=f"`{cls.gen_team_name(r, arg)}`")

    @staticmethod
    def gen_team_name(r, starts_with):
        return f"{r.word(starts_with=starts_with, include_parts_of_speech=['adjective']).title()} {r.word(starts_with=starts_with, include_parts_of_speech=['nouns']).title()}"

    letters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
