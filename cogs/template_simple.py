# cogs/template_simple.py

import discord
from discord.ext import commands, tasks

class TemplateSimple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    cog = TemplateSimple(bot)
    await bot.add_cog(cog)