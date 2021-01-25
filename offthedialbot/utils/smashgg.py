"""Contains requests."""

from offthedialbot import env, utils


async def post(query, variables, ctx=None):
    """Send a post request to the smash.gg gql api."""
    ver = 'alpha'
    url = 'https://api.smash.gg/gql/' + ver
    headers = {"Authorization": f"Bearer {env['smashgg']}"}
    request = {
        "query": query,
        "variables": variables
    }
    async with utils.session.post(url, json=request, headers=headers) as resp:
        if resp.status != 200 and ctx:
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title=f"Status Code - `{resp.status}`",
                description="An error occurred while trying to retrieve tournament data from smash.gg, try again later.")
            raise utils.exc.CommandCancel

        return resp.status, await resp.json()
