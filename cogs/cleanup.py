# cogs/spam_delete.py

from discord.ext import commands
from core.omega import omega

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clean')
    async def clean(self, ctx, amount):
        """
        Deletes the specified number of messages from the channel.
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the required permissions for that command.")
            return

        if amount == 'all':
            await ctx.channel.purge(limit=None)
            await ctx.send("Deleted all messages.", delete_after=5)
            return

        if amount is None or not amount.isdigit():
            await ctx.send("Specify a valid amount of messages to delete.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    
async def setup(bot):
    await bot.add_cog(Cleanup(bot))