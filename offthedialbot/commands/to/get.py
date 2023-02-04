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
            d = user.discord(ctx.bot)
            if d:
                name, mention = d.name, d.mention
            else:
                name, mention = user.id, "N/A"

            embed = discord.Embed(
                title=name,
                description="\n".join([
                    f"`User Mention:   ` **{mention}**",
                    f"`SplashTag:      ` **`{user.dict['profile']['splashtag']}`**",
                    f"`SW:             ` **`{user.dict['profile']['sw']}`**",
                    f"`Rank:           ` **`{user.get_rank()}`**",
                    f"`Weapons:        ` \n> {user.get_weapons()}",
                    f"`Competitive Exp:` \n> {user.dict['profile']['cxp']}",
                    f"`Smash.gg Info:  ` **`{(await user.smashgg())['player']['gamerTag']}`** **(`{user.dict['profile']['slug']}`)**",
                    f"`Signal Strength:` **`{user.dict['meta']['signal']}`**",
                ]))
            await utils.CommandUI.create_ui(ctx, embed)
        except KeyError:
            await utils.CommandUI.create_ui(ctx, discord.Embed(
                title=name,
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
                f"`Signup Date:  ` **`{signup.dict['signupDate']}`**",
                f"`Modified Date:` **`{signup.dict['modifiedDate']}`**",
                f"`Timezone:     ` **`{signup.dict['timezone']}`**",
            ]))
        await utils.CommandUI.create_ui(ctx, embed)
