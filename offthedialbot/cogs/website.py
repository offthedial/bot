"""cogs.Website"""

import re
import asyncio
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

    @commands.command()
    async def faq(self, ctx, *, section):
        """Send an embedded section of the faq."""
        await self.send_embedded_section(ctx, "faq", section, 4)

    @commands.group(aliases=["d", "docs"], invoke_without_command=True)
    async def rules(self, ctx, *, section: str = None):
        """Send an embedded section of a rules page."""
        if not discord.utils.get(ctx.author.roles, name="Staff"):
            raise utils.exc.CommandCancel(title="Permission Denied", description=f"If you're looking for the rules, please use https://otd.ink/idtga/rules")
        tourney = utils.Tournament()
        if section:
            await self.send_embedded_section(ctx, f"{tourney.dict['type']}/rules", section)
        else:
            lines = (await self.get_page(ctx, f"{tourney.dict['type']}/rules")).splitlines()
            for header in self.list_headers(lines, 2, strict=True):
                await self.send_embedded(ctx, lines, header, f"{tourney.dict['type']}/rules")
                await asyncio.sleep(0.2)

    @rules.command()
    async def idtga(self, ctx, *, section):
        """Send an embedded section of a idtga rules page."""
        await self.send_embedded_section(ctx, f"idtga/rules", section)

    @rules.command()
    async def wl(self, ctx, *, section):
        """Send an embedded section of a wl rules page."""
        await self.send_embedded_section(ctx, f"wl/rules", section)

    async def send_embedded_section(self, ctx, page, section, minimal=2):
        lines = (await self.get_page(ctx, page)).splitlines()
        header = self.get_header(self.list_headers(lines, minimal), section)

        if header is None:
            raise utils.exc.CommandCancel(title="No section found", description="Could not find a section that resembled what you entered, try rewording what you said.")

        await self.send_embedded(ctx, lines, header[0], page)

    async def send_embedded(self, ctx, lines, header, page):
        name, section = self.get_section(lines, header)
        header_link = re.sub(r' ', "-", re.sub(r'[^A-Za-z0-9 ]', "", name)).lower()
        await self.display_section(ctx, name, section[None], f"https://otd.ink/{page}#{header_link}")
        for key, value in section.items():
            if key is not None:
                await self.display_section(ctx, key, value)

    @staticmethod
    async def display_section(ctx, name, section, url=None):
        section = re.sub(r'<\/?[^<\/>]+>', '', "\n".join(section))
        embed = discord.Embed(description=section, color=utils.colors.BOT)
        if url:
            embed.url = url
            embed.title = name
        else:
            embed.set_author(name=name)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Section too long!", description="Try narrowing down your search to a more specific sub-section.")

    @staticmethod
    async def get_page(ctx, slug: str):
        async with utils.session.get(f"https://raw.githubusercontent.com/offthedial/site/master/src/pages/{slug}.md") as resp:
            if resp.status != 200:
                raise utils.exc.CommandCancel(
                    title=f"Status Code - `{resp.status}`",
                    description="An error occurred while trying to retrieve website data from otd.ink, check the status code or try again later.")
            return await resp.text()

    @staticmethod
    def get_section(lines, header):
        name = header.split()
        header_hashes = len(name[0])
        subsection = None
        section = {
            None: [],
        }
        for line in lines[lines.index(header)+1:]:
            if line.startswith("#"):
                line_hashes = len(line.split()[0])
                if line_hashes == header_hashes + 1:
                    subsection = ' '.join(line.split()[1:])
                    section[subsection] = []
                    line = False
                elif line_hashes > header_hashes:
                    line = f"__**{' '.join(line.split()[1:])}**__"
                else:
                    break
            if line is not False:
                section[subsection].append(line)
        return " ".join(name[1:]), section

    @staticmethod
    def list_headers(lines, minimal, strict = False):
        prefix = '#'*minimal
        if strict:
            prefix += " "
        return [line for line in lines if line.startswith(prefix)]

    @staticmethod
    def get_header(headers, choice):
        """Fuzzy search header."""
        partial_filter = process.extract(choice, headers, fuzz.partial_ratio, score_cutoff=75)
        return process.extractOne(choice, [result[0] for result in partial_filter], fuzz.ratio)
