from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot, omega):
        self.bot = bot
        self.omega = omega

    @commands.command()
    async def example(self, ctx):
        await ctx.send("This command has access to the Omega class!")