"""$to count"""
from offthedialbot import utils


class ToCount(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, collection: str = "signups"):
        """Count the current number of signups or subs."""
        async with ctx.typing():
            tourney = utils.Tournament()
            if collection != "subs":
                stream = tourney.signups(ignore_ended=True)
            else:
                stream = tourney.subs(ignore_ended=True)
            count = len(list(stream))

        description = f"**Total {collection}:** `{str(count)}`"
        if collection == 'signups':
            description = description + "\n" + f'**Total teams:** `{str(int(count / 4))}`, with `{str(count % 4)}` extra.'
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title=f"{collection.capitalize()} Count",
            description=description)
