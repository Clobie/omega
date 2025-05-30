# cogs/reactor.py

from discord.ext import commands
import random
from core.omega import omega

class Reactor(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.respond_chance = 5

    async def react_gif(self, message):
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        react_gif_url = await omega.gfy.get_react_gif_url(prompt)
        await message.channel.send(react_gif_url)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        if omega.common.chance(self.respond_chance):
            functions = [self.react_gif]
            selected_function = random.choice(functions)
            await selected_function(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactor(bot))
