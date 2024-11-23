import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))