import utils


async def main(ctx):
    """Test command to create a mock profile for the user instantly."""
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
        "style_points": ["flex", "slayer"],  # Groups A, B, and C.
        "cxp": 22,
        "meta": {
            "currently_competing": False,
            "previous_tourneys": [],
            "dropout_ban": None,
        }
    }
    utils.dbh.new_profile(profile, ctx.author.id)
    await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Created mock profile", description="Located under name: `Dave`")
