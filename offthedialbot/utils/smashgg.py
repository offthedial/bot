"""test smashgg"""
from offthedialbot import env, utils


ver = 'alpha'

tournament_query = """query TournamentQuery($slug: String) {
  tournament(slug: $slug){
    name
    startAt
  }
}"""


async def post(query):
    """Send a post request to the smash.gg gql api."""
    slug = utils.tourney.links[utils.tourney.get()['type']].split('/')[-1]
    url = 'https://api.smash.gg/gql/' + ver
    headers = {"Authorization": f"Bearer {env['smashgg']}"}
    request = {
        "query": query,
        "variables": {"slug": slug}
    }
    async with utils.session.post(url, json=request, headers=headers) as resp:
        return resp.status, await resp.json()
