import utils


async def main(ctx):
    """Test command to create a mock profile for the user instantly."""
    await utils.CommandUI.check_pemissions(ctx, required_roles={"moderator": True})
    profile: dict = {
        "status": {
            "IGN": "Dave",
            "SW": 111100000000,
            "Ranks": {
                "Splat Zones": 1000,
                "Rainmaker": 2500.0,
                "Tower Control": 1355.6,
                "Clam Blitz": 1260.8,
            },
        },
        "stylepoints": ["flex", "slayer"],  # Groups A, B, and C.
        "cxp": 22,
        "meta": {
            "competing": True,
            "previous_tourneys": [],
            "banned": None,
        }
    }
    utils.dbh.new_profile(profile, ctx.author.id)
    await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Created mock profile", description="Located under name: `Dave`")
