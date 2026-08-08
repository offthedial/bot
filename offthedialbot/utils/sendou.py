"""Contains functions to call the sendou.ink public API."""

from offthedialbot import utils, env, logger
from .session import session

BASE = 'https://sendou.ink/api'


async def request(path, method='GET', body=None, ctx=None, auth=True):
    """Send a request to the sendou.ink api, return (status, data).

    Pass ctx to raise CommandCancel on failure instead of returning the status.
    Callers that want to handle a failure themselves must omit ctx and check
    the status, in which case data holds sendou's error message as text.
    """
    headers = {}
    if auth:
        headers["Authorization"] = f"Bearer {env.get('sendou')}"

    async with session.request(method, BASE + path, json=body, headers=headers) as resp:
        data = await resp.json() if resp.content_type == 'application/json' else await resp.text()
        if ctx and resp.status not in (200, 204):
            raise utils.exc.CommandCancel(
                title=f"Status Code - `{resp.status}`",
                description=f"Unable to reach `{path}` on sendou.ink, try again later.")
        return resp.status, data


async def tournament(id, ctx=None):
    """GET /tournament/{id} - name, startTime, team counts, brackets, isFinalized."""
    status, data = await request(f"/tournament/{id}", ctx=ctx)
    return data


async def teams(id, ctx=None):
    """GET /tournament/{id}/teams - rosters, including each member's discordId."""
    status, data = await request(f"/tournament/{id}/teams", ctx=ctx)
    return data


async def standings(id, idx, ctx=None):
    """GET /tournament/{id}/brackets/{idx}/standings - placements per team id."""
    status, data = await request(f"/tournament/{id}/brackets/{idx}/standings", ctx=ctx)
    return data


async def remove_member(id, team_id, user_id, ctx=None):
    """POST /tournament/{id}/teams/{teamId}/remove-member. Needs the write token.

    Sendou refuses to remove the team owner, or anyone who has already played
    a set once the tournament has begun.
    """
    return await request(f"/tournament/{id}/teams/{team_id}/remove-member",
                         method='POST', body={"userId": user_id}, ctx=ctx)


async def add_member(id, team_id, user_id, ctx=None):
    """POST /tournament/{id}/teams/{teamId}/add-member. Needs the write token.

    Sendou refuses players who are banned, already on a team, or missing a
    friend code / in-game name the tournament requires.
    """
    return await request(f"/tournament/{id}/teams/{team_id}/add-member",
                         method='POST', body={"userId": user_id}, ctx=ctx)


async def user_id(discord_id):
    """GET /user/{discordId}/ids - resolve a discord id to a sendou.ink user id.

    The only endpoint on the public api that takes no token, which is why the
    site can call it straight from the browser too.

    Returns None when the discord account has no sendou.ink profile. Anything
    other than a 200 or 404 is an outage rather than an answer, so it raises -
    otherwise a sendou.ink hiccup would read as 'nobody has an account'.
    """
    status, data = await request(f"/user/{discord_id}/ids", auth=False)
    if status == 404:
        return None
    if status != 200:
        raise utils.exc.CommandCancel(
            title=f"Status Code - `{status}`",
            description="Unable to look up sendou.ink accounts, try again later.")
    return data["id"]


async def find_team(id, discord_id, ctx=None):
    """Return (team, member) for a discord id in a tournament, or (None, None)."""
    for team in await teams(id, ctx=ctx):
        for member in team["members"]:
            if member["discordId"] == str(discord_id):
                return team, member
    return None, None


async def rounds(id, brackets, ctx=None):
    """Return [(bracket name, [maps per round])], the replacement for start.gg's bestOf.

    A bracket can hold several groups - winners, losers, grands - and each one
    numbers its rounds from 1, so they can't be told apart by number alone.
    start.gg read the first phase group only, so take the first group here too.

    maps.type (BEST_OF vs PLAY_ALL) is ignored on purpose: either way the round
    needs maps.count stages prepared.
    """
    result = []
    for idx, meta in enumerate(brackets):
        status, data = await request(f"/tournament/{id}/brackets/{idx}", ctx=ctx)
        group = data["round"][0]["groupId"] if data["round"] else None
        counts = []
        for round in sorted((r for r in data["round"] if r["groupId"] == group),
                            key=lambda r: r["number"]):
            if not (maps := round.get("maps")):
                raise utils.exc.CommandCancel(
                    title="Round format not set",
                    description=f"`{meta['name']}` round {round['number']} has no map count on sendou.ink.")
            counts.append(maps["count"])
        result.append((meta["name"], counts))
    return result
