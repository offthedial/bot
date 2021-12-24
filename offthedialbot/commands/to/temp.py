"""$to temp"""
from offthedialbot import utils


class ToTemp(utils.Command):
    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, confirm=False):
        """Replace each document in the collection."""
        docs = utils.db.collection("users").stream()
        batch = utils.db.batch()
        for doc in docs:
            profile_data = doc.to_dict()["profile"]

            # find rank with the highest power and return rank
            rank = (
                max(
                    profile_data["ranks"].values(),
                    key=lambda x: utils.User.rank_to_power(x),
                )
                if profile_data.get("ranks")
                else None
            )

            # create new profile object
            profile = {
                "ign": profile_data.get("ign"),
                "sw": profile_data.get("sw"),
                "rank": rank,
                "weapons": None,
                "cxp": None,
                "smashgg": None
                if not profile_data.get("smashgg")
                else f"smash.gg/user/{profile_data['smashgg']}",
            }
            batch.update(doc.reference, {"profile": profile})

            print(profile)
