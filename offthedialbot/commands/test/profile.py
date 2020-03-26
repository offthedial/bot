"""$test profile"""
from offthedialbot import utils


@utils.deco.require_role("Developer")
async def main(ctx):
    """Create a mock profile for the user."""
    profile: dict = {
        "_id": ctx.author.id,
        "status": {
            "IGN": "Dave",
            "SW": '048922225689',
            "Ranks": {
                "Splat Zones": 2000,
                "Tower Control": 1355.6,
                "Rainmaker": 2500.0,
                "Clam Blitz": 1260.8,
            },
        },
        "stylepoints": ["flex", "slayer"],  # Groups A, B, and C.
        "cxp": 22,
        "signal_strength": 150,
    }
    profilemeta: dict = {
        "_id": ctx.author.id,
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
