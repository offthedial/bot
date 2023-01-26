"""$to whitelist"""
import discord
from firebase_admin import firestore

from offthedialbot import utils


class ToWhitelist(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, user_id = None, remove: bool = False):
        """Display the current whitelist.

        To add someone to the whitelist, specify a discord id when calling the command.
        To remove someone from the whitelist, specify their discord id, and attach "true" to the end when calling the command.
        """
        tourney = utils.Tournament()

        if not user_id:
            # Send whitelist
            return await utils.Alert(ctx, utils.Alert.Style.INFO,
                title=f"Here's the current whitelist:",
                description="\n".join([
                    f"- <@{i}> (`{i}`)" for i in tourney.dict["whitelist"]
                ]))

        # Modify whitelist
        Method = firestore.ArrayRemove if remove else firestore.ArrayUnion
        tourney.ref.update({"whitelist": Method([f"{str(user_id)}"])})
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title=f"Updated Whitelist",
            description=f"{'Removed' if remove else 'Added'} `{user_id}` {'from' if remove else 'to'} whitelist.")
