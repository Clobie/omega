import discord
from discord.ext import commands
from utils.cog import Cog
import re

class ExperimentalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog = Cog()

    @commands.command(name='test_cog')
    async def test_cog(self, ctx, cog_name: str, *, message: str):
        """
        Test an experimental cog.
        Usage: !test_cog <cog_name> \`\`\`code\`\`\`
        """
        # Regex to extract code blocks
        code_matches = re.findall(r'\`\`\`(.*?)\`\`\`', message, re.DOTALL)
        
        if not code_matches:
            await ctx.send("Please provide the code wrapped in triple backticks.")
            return

        cog_data = code_matches[0].strip()  # The first code block is the cog data
        
        response = await self.cog.test_cog_experimental(self.bot, cog_name, cog_data)
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(ExperimentalCog(bot))