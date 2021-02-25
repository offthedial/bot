"""$to get"""
import discord

from offthedialbot import utils


class ToGet(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, user: discord.User):
        """Retrieve the profile and signup of a user."""
        user = utils.User(user.id)
        await cls.send_user_embed(ctx, user)
        await cls.send_signup_embed(ctx, user)

    @classmethod
    async def send_user_embed(cls, ctx, user: utils.User):
        if not user.doc.exists:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="User doesn't have an account!")
        try:
            embed = discord.Embed(
                title=user.discord(ctx.bot).name,
                description="\n".join([
                    f"`User mention:       ` {user.discord(ctx.bot).mention}",
                    f"`Smash.gg slug & tag:` **`{user.dict['profile']['smashgg']}`** & **`{(await user.smashgg())['player']['gamerTag']}`**",
                    f"`IGN:                ` **`{user.dict['profile']['ign']}`**",
                    f"`SW:                 ` **`{user.dict['profile']['sw']}`**",
                    f"`Ranks (SZ/TC/RM/CB):` **`{' / '.join(user.get_ranks())}`**",
                    f"`ELO:                ` **`{user.get_elo()}`**",
                    f"`Playstyle (A/S/M/F):` **`{' / '.join([str(p) for p in user.get_playstyles()[::2]])}`**",
                    f"`Amount of tourneys: ` **`{user.dict['profile']['cxp']['amount']}`**",
                    f"`Highest placement:  ` **`{user.dict['profile']['cxp']['placement']}`**",
                    f"`Signal Strength:    ` **`{user.dict['meta']['signal']}`**",
                ]))
            await utils.CommandUI.create_ui(ctx, embed)
        except KeyError:
            await utils.CommandUI.create_ui(ctx, discord.Embed(
                title=user.discord(ctx.bot).name,
                description=f"```\n{user.dict}\n```"))

    @classmethod
    async def send_signup_embed(cls, ctx, user: utils.User):
        signup = user.signup(ignore_ended=True)
        if not signup:
            return
        embed = discord.Embed(
            color=utils.colors.COMPETING,
            title=signup.col.capitalize(),
            description="\n".join([
                f"`Smash.gg reg tag: ` **`{await signup.smashgg(user)}`**",
                f"`Timezone offset:  ` **`{signup.dict['tzOffset']}`**",
                f"`Confirmation code:` **`{signup.dict['confirmationCode']}`**",
            ]))
        await utils.CommandUI.create_ui(ctx, embed)
