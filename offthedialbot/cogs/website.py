"""cogs.Website"""
from fuzzywuzzy import fuzz, process

import discord
from discord.ext import commands

from offthedialbot import utils


class Website(commands.Cog):

    @commands.group(invoke_without_command=True, aliases=["web", "site", "docs", "d"])
    async def website(self, ctx, *args):
        """Send an embedded section of an otd.ink page."""

    @website.command()
    async def faq(self, ctx, *, section):
        """Send an embedded section of the faq."""
        await self.send_embedded_section(ctx, "faq", section, "### ")

    @website.group(aliases=["tourney", "t"])
    async def tournament(self, ctx, page, sub, *, section):
        """Send an embedded section of a tournament page."""
        await self.send_embedded_section(ctx, f"{page}/{sub}", section, "## ")

    async def send_embedded_section(self, ctx, page, section, startwith=None):
        lines = (await self.get_page(ctx, page)).splitlines()
        name, content = self.get_section(self.create_sections(lines, startwith), section)
        if name is None:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="No section found.", description="Could not find a section that resembled what you entered, try rewording what you said.")
            raise utils.exc.CommandCancel
        await self.display_section(ctx, f"https://otd.ink/{page}", name, content)

    @staticmethod
    async def display_section(ctx, url, name, content):
        embed = discord.Embed(title=name, description=content, color=utils.colors.DIALER)
        embed.url = url
        await ctx.send(embed=embed)

    @staticmethod
    async def get_page(ctx, slug: str):
        async with utils.session.get(f"https://raw.githubusercontent.com/LeptoFlare/otd.ink/master/{slug}.md") as resp:
            if resp.status != 200:
                await utils.Alert(ctx, utils.Alert.Style.DANGER,
                    title=f"Status Code - `{resp.status}`",
                    description="An error occurred while trying to retrieve website data from otd.ink, try again later.")
                raise utils.exc.CommandCancel
            return await resp.text()
    
    @staticmethod
    def create_sections(lines, startwith="## "):
        sections = {
            "": []
        }
        for line in lines:
            if line.startswith(startwith):
                sections[line] = []
            else:
                if not line.startswith("".join(startwith[1:])):
                    if line.startswith("#"):
                        line = f"__**{' '.join(line.split()[1:])}**__"
                    sections[list(sections)[-1]].append(line)
        return sections

    @staticmethod
    def get_section(sections, choice):
        if not (result := process.extractOne(choice, list(sections), scorer=fuzz.partial_ratio, score_cutoff=51)):
            return None, None

        section = sections[result[0]]
        return " ".join(result[0].split()[1:]), "\n".join(section)

    @commands.command(hidden=True)
    @utils.deco.require_role("Organiser")
    async def moved(self, ctx, page: str):
        """This channel has been moved!"""
        await utils.Alert(ctx, utils.Alert.Style.WARNING,
            title="This page has been moved! :construction_site:",
            description=f"Soon this channel will be gone, you can find the new and updated version here:\n**https://otd.ink/{page}**")
