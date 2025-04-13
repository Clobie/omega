# cogs/inviteme.py

from discord.ext import commands
from core.omega import omega

class InviteMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inviteme")
    async def inviteme(self, ctx):
        """
        Generate an invite link for the bot.
        """
        await ctx.send(f"https://discord.com/oauth2/authorize?client_id={omega.cfg.INVITE_ID}")

async def setup(bot):
    await bot.add_cog(InviteMe(bot))