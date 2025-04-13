# cogs/cleanup.py

from discord.ext import commands
from core.omega import omega
import datetime
from dateutil import parser

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def parse_flexible_date(val: str):
        try:
            return parser.parse(val, dayfirst=False).date()
        except ValueError:
            return None
     
    @commands.command(name='clean')
    async def clean(self, ctx, *, val):
        """
        Deletes the specified number of messages from the channel.
        """

        await ctx.message.delete()

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You do not have the required permissions for that command.")
            return

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            deleted = await ctx.channel.purge(limit=None, check=lambda m: m.author == user)
            await ctx.send(f"Deleted {len(deleted)} messages from {user.mention}.\n*This message will delete in 5 seconds.*", delete_after=5)
            return
        
        if val == 'bots':
            deleted = await ctx.channel.purge(limit=None, check=lambda m: m.author.bot)
            await ctx.send(f"Deleted {len(deleted)} messages from bots.\n*This message will delete in 5 seconds.*", delete_after=5)
            return

        if val == 'all':
            deleted = await ctx.channel.purge(limit=None)
            await ctx.send(f"Deleted {len(deleted)} messages.\n*This message will delete in 5 seconds.*", delete_after=5)
            return

        if val == 'images':
            await ctx.channel.purge(limit=None, check=lambda m: m.attachments)
            await ctx.send("Deleted all images.\n*This message will delete in 5 seconds.*", delete_after=5)
            return

        if val == 'today':
            await ctx.channel.purge(limit=None, check=lambda m: m.created_at.date() == datetime.datetime.utcnow().date())
            await ctx.send("Deleted all messages from today.\n*This message will delete in 5 seconds.*", delete_after=5)
            return

        if val.isdigit():
            deleted = await ctx.channel.purge(limit=int(val))
            await ctx.send(f"Deleted {len(deleted)} messages.\n*This message will delete in 5 seconds.*", delete_after=5)
            return

        date = self.parse_flexible_date(val)
        if date:
            try:
                await ctx.channel.purge(limit=None, check=lambda m: m.created_at.date() == date)
                await ctx.send(f"Deleted all messages from {date}.\n*This message will delete in 5 seconds.*", delete_after=5)
            except Exception as e:
                await ctx.send(f"An error occurred while purging messages: {e}", delete_after=5)
            return
        
        deleted = await ctx.channel.purge(limit=None, check=lambda m: m.content == val)
        await ctx.send(f"Deleted {len(deleted)} messages matching '{val}'.\n*This message will delete in 5 seconds.*", delete_after=5)
    
async def setup(bot):
    await bot.add_cog(Cleanup(bot))