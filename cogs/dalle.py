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
from utils.credit import credit

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = "dall-e-3"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        if credit.get_user_credits(ctx.author.id) < 4:
            await ctx.send(f"You don't have enough credits for that :(")
            return
        reply_msg = await ctx.send(self.thinking_emoji)
        image_url = ai.generate_image(self.model, prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    filename = common.generate_random_string() + "_image.png"
                    file = discord.File(io.BytesIO(image_data), filename=filename)
                    footer = ai.get_footer('null', 0.04)
                    ai.update_cost_static(0.04)
                    credits = credit.convert_cost_to_credits(0.04)
                    credit.user_spend(ctx.author.id, credits)
                    await status.update(self.bot, 'watching', f"Cost: ${ai.get_total_cost()}")
                    await reply_msg.edit(content=footer, attachments=[file])

async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))