# cogs/cleanup.py

from discord.ext import commands
from core.omega import omega

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clean')
    async def clean(self, ctx, val):
        """
        Deletes the specified number of messages from the channel.
        """
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the required permissions for that command.")
            return

        if val == 'all':
            await ctx.channel.purge(limit=None)
            await ctx.send("Deleted all messages.", delete_after=5)
            return

        if val == 'images':
            await ctx.channel.purge(limit=None, check=lambda m: m.attachments)
            await ctx.send("Deleted all images.", delete_after=5)
            return

        if val is None or not val.isdigit():
            await ctx.send("Specify a valid amount of messages to delete.")
            return

        deleted = await ctx.channel.purge(limit=val)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    
async def setup(bot):
    await bot.add_cog(Cleanup(bot))