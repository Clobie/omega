# cogs/dalle.py

import discord
from discord.ext import commands
import aiohttp
import io
from utils.ai import ai
from utils.common import common
from utils.config import cfg
from utils.log import logger
from utils.status import status

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = "dall-e-3"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        reply_msg = await ctx.send(self.thinking_emoji)
        image_url = ai.generate_image(self.model, prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    file = discord.File(io.BytesIO(image_data), filename="image.png")
                    footer = ai.get_footer('null', 0.04)
                    ai.update_cost_static(0.04)
                    await status.update(self.bot, f"Cost: ${ai.get_total_cost()}")
                    await reply_msg.edit(content=footer, attachments=[file])

async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))