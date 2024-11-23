 # cogs/dalle.py

import discord
from discord.ext import commands
import random
import logging
import requests
import aiohttp
import io
import utils.config
import utils.ai as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        reply_msg = await ctx.send("<a:ai_thinking:1309172561250353224>")
        image_url = self.ai.generate_image(prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    file = discord.File(io.BytesIO(image_data), filename="image.png")
                    await reply_msg.edit(content='', attachments=[file])

async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))