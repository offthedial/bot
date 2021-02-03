"""Contains function to create ClientSession."""

from offthedialbot import utils, env, logger
import aiohttp


session = aiohttp.ClientSession()
logger.debug("New ClientSession has been created.")


def use_type(type):
    """Use graphql query type."""
    if type == "smashgg":
        ver = 'alpha'
        url = 'https://api.smash.gg/gql/' + ver
        headers = {"Authorization": f"Bearer {env['smashgg']}"}
        return url, headers

    if type == "sendou":
        url = 'https://sendou.ink/graphql'
        return url, {}


async def graphql(type, query, variables={}, ctx=None):
    """Send a post request to the smash.gg gql api."""
    request = {
        "query": query,
        "variables": variables
    }
    url, headers = use_type(type)
    async with session.post(url, json=request, headers=headers) as resp:
        if ctx:
            if resp.status != 200:
                raise utils.exc.CommandCancel(
                    title=f"Status Code - `{resp.status}`",
                    description=f"Unable to make a request for type '{type}', try again later.")
            if errors := (await resp.json()).get("errors", None):
                raise utils.exc.CommandCancel(
                    title=f"GraphQL Request Failed",
                    description=f"```json\n{errors}\n```")

        return resp.status, await resp.json()
