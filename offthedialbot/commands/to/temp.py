"""$to temp"""
from offthedialbot import utils


class ToTemp(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, confirm=False):
        """Replace each document in the collection."""
        docs = utils.db.collection(u'users').stream()
        batch = utils.db.batch()
        for doc in docs:
            profile_data = doc.to_dict()["profile"]

            # find rank with the highest power and return rank
            all_powers = [utils.User.rank_to_power(rank) for rank in profile_data["ranks"].values()]
            highest_power = max(all_powers)
            rank = [rank for rank in profile_data["ranks"].values() if utils.User.rank_to_power(rank) == highest_power][0]

            # create new profile object
            profile = {
                "ign": profile_data["ign"],
                "sw": profile_data["sw"],
                "rank": rank,
                "weapons": None,
                "cxp": None,
                "smashgg": f"smash.gg/user/{profile_data['smashgg']}"
            }
            batch.update(doc.reference, {"profile": profile})

            print(profile)
