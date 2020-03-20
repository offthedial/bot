"""$test mutate"""
from offthedialbot import utils


@utils.deco.require_role("Developer")
async def main(ctx):
    """Mutate all the profiles in the collection."""
    [print(d) for d in utils.dbh.profiles.find({})]
    utils.dbh.profiles.update_many({}, {"$set": {"meta.confirmation_code": None}})
    [print(d) for d in utils.dbh.profiles.find({})]
