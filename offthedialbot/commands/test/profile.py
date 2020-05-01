"""$test profile"""
from offthedialbot import utils


class TestProfile(utils.Command):
    """Create a mock profile for the user."""

    @classmethod
    @utils.deco.require_role("Developer")
    async def main(cls, ctx):
        """Create a mock profile for the user."""
        profile: dict = {
            "_id": ctx.author.id,
            "IGN": "Dave",
            "SW": '048922225689',
            "Ranks": {
                "Splat Zones": 2000,
                "Tower Control": 1355.6,
                "Rainmaker": 2500.0,
                "Clam Blitz": 1260.8,
            },
            "stylepoints": ["flex", "slayer"],  # Groups A, B, and C.
            "cxp": 22,
        }
        profilemeta: dict = {
            "_id": ctx.author.id,
            "signal": 150,
            "banned": None,
            "smashgg": None,
            "reg": {
                "reg": False,
                "code": None
            }
        }
        utils.dbh.profiles.replace_one({"_id": ctx.author.id}, profile, upsert=True)
        utils.dbh.metaprofiles.replace_one({"_id": ctx.author.id}, profilemeta, upsert=True)

        await utils.Alert(
            ctx, utils.Alert.Style.SUCCESS,
            title="Created mock profile", description="Located under name: `Dave`"
        )
