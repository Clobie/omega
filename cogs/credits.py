# cogs/template.py

import os
import discord
from discord.ext import commands
from core.omega import omega

class Credits(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, total = 10):
        toplist = omega.credit.get_leaderboard(total)
        await ctx.send(toplist)

    @commands.command(name='credits')
    async def credits(self, ctx, user: discord.User = None):
        """
        See how many credits you or another user has
        """
        user_id = user.id if user else ctx.author.id
        credits = omega.credit.get_user_credits(user_id)
        user_name = user.name if user else ctx.author.name
        await ctx.send(f"{user_name} has {credits} credits.")

    @commands.command(name='give')
    async def give(self, ctx, amount: float, member: discord.Member):
        """
        Give credits to another user
        """
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to give.")
            return
        user_from_id = ctx.author.id
        user_to_id = member.id
        if omega.credit.give_user_credits(user_from_id, user_to_id, amount):
            await ctx.send(f"You've given {amount} credits to {member.mention}.")
        else:
            await ctx.send("You don't have enough credits.")
    
    @commands.command(name='gift')
    async def gift(self, ctx, amount: float, member: discord.Member):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to give.")
            return
        if omega.credit.gift_user_credits(member.id, amount):
            await ctx.send(f"You've given {amount} credits to {member.mention}.")
    
    @commands.command(name='take')
    async def take(self, ctx, amount: float, user: discord.Member):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to take.")
            return
        if omega.credit.take_user_credits(user.id, amount):
            await ctx.send(f"You've taken {amount} credits from {user.mention}.")
        else:
            await ctx.send(f"Failed to take credits from {user.mention}. They may not have enough credits.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Credits(bot))