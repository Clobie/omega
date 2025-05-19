# cogs/dalle.py

import io
import aiohttp
import discord
from discord.ext import commands
from core.omega import omega

class Dalle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = "dall-e-3"
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.base_cost = 0.04
        self.base_profit = 0.01
        self.total_cost = self.base_cost + self.base_profit

    @commands.command(name='generate')
    async def generate_image(self, ctx, *, prompt):
        """
        Generate an image using DALL-E 3.
        """
        if int(omega.credit.get_user_credits(ctx.author.id)) < 5:
            await ctx.send(f"You don't have enough credits for that :(")
            return
        reply_msg = await ctx.send(self.thinking_emoji)
        image_url = omega.ai.generate_image(self.model, prompt)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    filename = omega.common.generate_random_string() + "_image.png"
                    file = discord.File(io.BytesIO(image_data), filename=filename)
                    footer = omega.ai.get_footer('null', self.total_cost)
                    omega.ai.update_cost_static(self.total_cost)
                    credits = omega.credit.convert_cost_to_credits(self.total_cost)
                    omega.credit.user_spend(ctx.author.id, credits)
                    omega.ai.log_usage(ctx.author.id, 0, self.total_cost, 'dalle3')
                    #await omega.status.update(self.bot, 'watching', f"Cost: ${omega.ai.get_total_cost()}")
                    await reply_msg.edit(content=footer, attachments=[file])

async def setup(bot: commands.Bot):
    await bot.add_cog(Dalle(bot))