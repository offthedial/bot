"""$to fix"""

from offthedialbot import utils
import json


class ToFix(utils.Command):
    """ Fix stylepoints mistake
    """

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Temporary fix command."""
        db = utils.firestore.db
        batch = db.batch()

        docs = db.collection(u'users').stream()
        for doc in docs:
            if "stylepoints" in doc.to_dict()["profile"].keys():
                stylepoints = doc.to_dict()["profile"]["stylepoints"]
                print(stylepoints)
                ref = db.collection(u'users').document(doc.id)
                batch.update(ref, {
                    u"profile.stylepoints.support": abs(stylepoints["aggressive"] - 10),
                    u"profile.stylepoints.objective": abs(stylepoints["slayer"] - 10),
                    u"profile.stylepoints.anchor": abs(stylepoints["mobile"] - 10),
                    u"profile.stylepoints.flex": abs(stylepoints["focused"] - 10),
                })
                print(doc.to_dict()["profile"]["stylepoints"])
            else:
                print(f"Skipped empty profile: {doc.id}")

        batch.commit()
