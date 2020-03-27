"""$test mutate"""
from offthedialbot import utils


@utils.deco.require_role("Developer")
async def main(ctx):
    profiles = utils.dbh.profiles.find({}, {"_id": True})
    for profile in profiles:
        pid = profile["_id"]
        metaprofile = utils.dbh.metaprofiles.find_one({"_id": pid})

        utils.dbh.profiles.update_one({"_id": pid}, {"$unset": {"signal": True}})
        utils.dbh.metaprofiles.replace_one({"_id": pid}, {
            "_id": pid,
            "signal": profile["signal"],
            "banned": metaprofile["banned"],
            "smashgg": metaprofile["smashgg"],
            "reg": metaprofile["reg"]})

    await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Mutate complete.", description="Remove this command as soon as possible")
