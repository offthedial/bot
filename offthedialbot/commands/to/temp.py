"""$to temp"""
from offthedialbot import utils


class FirestoreAutoWriteBatch:
    def __init__(self, batch, limit=100, auto_commit=True):
        self._batch = batch
        self._limit = limit
        self._auto_commit = auto_commit
        self._count = 0

    def create(self, *args, **kwargs):
        self._batch.create(*args, **kwargs)
        self._count += 1

        if self._auto_commit:
            self.commit_if_limit()

    def set(self, *args, **kwargs):
        self._batch.set(*args, **kwargs)
        self._count += 1

        if self._auto_commit:
            self.commit_if_limit()

    def update(self, *args, **kwargs):
        self._batch.update(*args, **kwargs)
        self._count += 1

        if self._auto_commit:
            self.commit_if_limit()

    def delete(self, *args, **kwargs):
        self._batch.delete(*args, **kwargs)
        self._count += 1

        if self._auto_commit:
            self.commit_if_limit()

    def commit(self, *args, **kwargs):
        self._batch.commit()
        self._count = 0

    def commit_if_limit(self):
        if self._count > self._limit:
            self._batch.commit()
            self._count = 0

            
class ToTemp(utils.Command):
    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, commit=False):
        """Replace each document in the collection."""
        docs = utils.db.collection("users").stream()
        batch = FirestoreAutoWriteBatch(utils.db.batch())

        for doc in docs:
            profile_data = doc.to_dict()["profile"]

            # create new profile object
            profile = { **profile_data }
            if smashgg_data := profile_data.get("smashgg"):
                profile["smashgg"] = smashgg_data[-22:]
            
            batch.update(doc.reference, {"profile": profile})

            print(profile)

        if commit:
            batch.commit()
            await ctx.send(
                embed=utils.Alert.create_embed(
                    style=utils.Alert.Style.SUCCESS, title="Committed changes"
                )
            )
        else:
            await ctx.send(
                embed=utils.Alert.create_embed(
                    style=utils.Alert.Style.SUCCESS, title="Changes not committed"
                )
            )
