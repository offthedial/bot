"""Contains requests."""

from offthedialbot import env, utils


ver = 'alpha'

startat = """query TournamentQuery($slug: String) {
  tournament(slug: $slug){
    name
    startAt
  }
}"""

registrationclosesat = """query TournamentQuery($slug: String) {
  tournament(slug: $slug){
    name
    registrationClosesAt
  }
}"""

totalgames = """query TournamentQuery($slug: String) {
  tournament(slug: $slug) {
    events {
      phases {
        name
        phaseGroups {
          nodes {
            rounds {
            	bestOf
            }
          }
        }
      }
    }
  }
}"""


async def post(query, slug, ctx=None):
    """Send a post request to the smash.gg gql api."""
    url = 'https://api.smash.gg/gql/' + ver
    headers = {"Authorization": f"Bearer {env['smashgg']}"}
    request = {
        "query": query,
        "variables": {"slug": slug}
    }
    async with utils.session.post(url, json=request, headers=headers) as resp:
        if resp.status != 200 and ctx:
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title=f"Status Code - `{resp.status}`",
                description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
            raise utils.exc.CommandCancel

        return resp.status, await resp.json()
