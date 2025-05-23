# cogs/template.py

import discord
from discord.ext import commands, tasks
from typing import Optional

class TemplateCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repeating_task.start()

    @tasks.loop(minutes=10.0)
    async def repeating_task(self):
        pass

    @repeating_task.before_loop
    async def before_repeating_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command(name='example')
    async def example_command(self, ctx, *, args):
        await ctx.send(f"Example command received with argument: {args}")

async def setup(bot: commands.Bot):
    cog = TemplateCog(bot)
    await bot.add_cog(cog)