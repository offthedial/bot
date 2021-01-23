"""cogs.Website"""

from rapidfuzz import fuzz, process

import discord
from discord.ext import commands

from offthedialbot import utils


class Website(commands.Cog):
    """All of the website-related commands."""

    @commands.command(invoke_without_command=True, aliases=["site"])
    async def website(self, ctx):
        """Send an embedded section of a page."""
        await ctx.send_help(ctx.cog)

    @commands.command(hidden=True)
    async def faq(self, ctx, *, section):
        """Send an embedded section of the faq."""
        await self.send_embedded_section(ctx, "faq", section, 4, partial=True)

    @commands.command(hidden=True, aliases=["d", "docs"])
    async def rules(self, ctx, page, *, section):
        """Send an embedded section of a rules page."""
        await self.send_embedded_section(ctx, f"{page}/rules", section)

    async def send_embedded_section(self, ctx, page, section, minimal=2, **kwargs):
        lines = (await self.get_page(ctx, page)).splitlines()
        header = self.get_header(self.list_headers(lines, minimal), section, **kwargs)

        if header is None:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="No section found.", description="Could not find a section that resembled what you entered, try rewording what you said.")
            raise utils.exc.CommandCancel

        name, content = self.get_section(lines, header[0])
        await self.display_section(ctx, f"https://otd.ink/{page}", name, content)

    @staticmethod
    async def display_section(ctx, url, name, content):
        embed = discord.Embed(title=name, description=content, color=utils.colors.DIALER)
        embed.url = url
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Section too long!", description="Try narrowing down your search to a more specific sub-section.")

    @staticmethod
    async def get_page(ctx, slug: str):
        async with utils.session.get(f"https://raw.githubusercontent.com/offthedial/site/master/src/pages/{slug}.md") as resp:
            if resp.status != 200:
                await utils.Alert(ctx, utils.Alert.Style.DANGER,
                    title=f"Status Code - `{resp.status}`",
                    description="An error occurred while trying to retrieve website data from otd.ink, check the status code or try again later.")
                raise utils.exc.CommandCancel
            return await resp.text()

    @staticmethod
    def get_section(lines, header):
        name = header.split()
        header_hashes = len(name[0])
        section = []
        for line in lines[lines.index(header)+1:]:
            if line.startswith("#"):
                line_hashes = len(line.split()[0])
                if line_hashes > header_hashes:
                    line = f"__**{' '.join(line.split()[1:])}**__"
                else:
                    break
            section.append(line)
        return " ".join(name[1:]), "\n".join(section)

    @staticmethod
    def list_headers(lines, minimal):
        return [line for line in lines if line.startswith("#"*minimal)]

    @staticmethod
    def get_header(headers, choice, partial=False):
        """Fuzzy search header."""
        scorer = fuzz.partial_ratio if partial else fuzz.token_sort_ratio
        return process.extractOne(choice, headers, scorer, score_cutoff=75)
