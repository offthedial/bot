"""$test profile"""
from offthedialbot import utils


@utils.deco.to_only
async def main(ctx):
    """Create a mock profile for the user."""
    profile: dict = {
        "_id": ctx.author.id,
        "status": {
            "IGN": "Dave",
            "SW": '048922225689',
            "Ranks": {
                "Splat Zones": 1000,
                "Rainmaker": 2500.0,
                "Tower Control": 1355.6,
                "Clam Blitz": 1260.8,
            },
        },
        "stylepoints": ["flex", "slayer"],  # Groups A, B, and C.
        "cxp": 22,
        "signal_strength": 150,
        "meta": {
            "competing": False,
            "smashgg": None,
            "banned": None,
        }
    }
    utils.dbh.profiles.replace_one({"_id": ctx.author.id}, profile, upsert=True)
    await utils.Alert(
        ctx, utils.Alert.Style.SUCCESS,
        title="Created mock profile", description="Located under name: `Dave`"
    )
