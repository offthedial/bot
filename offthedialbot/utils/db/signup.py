from offthedialbot import utils
from . import Tournament


class Signup:
    """Represents what useSignup would be."""

    def __init__(self, id, user, tourney=None):
        self.id = str(id)
        self.user = user
        self.tourney = tourney if tourney else Tournament()

        if not isinstance(self.id, (int, str)):
            self.set_signup(self.id)
            return

        self.doc = self.tourney.signups(col=True).document(self.id).get()
        if self.doc.exists:
            self.set_signup()
            return

        self.doc = self.tourney.subs(col=True).document(self.id).get()
        if self.doc.exists:
            self.set_signup()
            return

        raise LookupError

    def set_signup(self):
        """Set signup self variables."""
        self.ref = self.doc.reference
        self.col = self.ref.parent.id
        self.dict = self.doc.to_dict()

    async def smashgg(self):
        """Get smash.gg data from the api with the user slug."""
        query = """query($slug: String) {
          tournament(slug: $slug) {
            participants(query: {perPage: 500}) {
              nodes {
                gamerTag
                user {
                  slug
                }
              }
            }
          }
        }"""
        status, data = await utils.graphql("smashgg", query, {"slug": self.tourney.dict["slug"]})
        for participant in data["data"]["tournament"]["participants"]["nodes"]:
            if participant["user"]["slug"][5:] == self.user.dict["profile"]["smashgg"]:
                return participant["gamerTag"]
