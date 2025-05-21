# cogs/template.py

import os
import discord
from discord.ext import commands
from core.omega import omega

class Credits(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_message_count = {}
        self.user_last_message_time = {}
        self.required_message_count_to_reward = 5
        self.message_reward_cooldown = 30  # seconds

    @commands.Cog.listener()
    async def on_ready(self):
        pass
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id

        # Initialize counters if not present
        if user_id not in self.user_message_count:
            self.user_message_count[user_id] = 0
        if user_id not in self.user_last_message_time:
            self.user_last_message_time[user_id] = message.created_at

        # Only count if 30 seconds have passed since last message
        if (message.created_at - self.user_last_message_time[user_id]).total_seconds() > self.message_reward_cooldown:
            self.user_last_message_time[user_id] = message.created_at
            self.user_message_count[user_id] += 1

            # Reward the user if they have sent enough messages
            if self.user_message_count[user_id] >= self.required_message_count_to_reward:
                self.user_message_count[user_id] = 0
                omega.credit.gift_user_credits(user_id, 5)
                await message.channel.send(
                    f"Hey {message.author.mention}, you just received 5 credits for being active! Use `!credits` to check your balance."
                )

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
    async def give(self, ctx, member: discord.Member, amount: int):
        """
        Give credits to another user
        """

        if not isinstance(member, discord.Member) or not isinstance(amount, int):
            await ctx.send("Command usage is !give @user amount")
            return

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
    async def gift(self, ctx, member: discord.Member, amount: int):
        if not isinstance(member, discord.Member) or not isinstance(amount, int):
            await ctx.send("Command usage is !gift @user amount")
            return
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to give.")
            return
        if omega.credit.gift_user_credits(member.id, amount):
            await ctx.send(f"You've given {amount} credits to {member.mention}.")
    
    @commands.command(name='take')
    async def take(self, ctx, member: discord.Member, amount: int):
        if not isinstance(member, discord.Member) or not isinstance(amount, int):
            await ctx.send("Command usage is !take @user amount")
            return
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to take.")
            return
        if omega.credit.take_user_credits(member.id, amount):
            await ctx.send(f"You've taken {amount} credits from {member.mention}.")
        else:
            await ctx.send(f"Failed to take credits from {member.mention}. They may not have enough credits.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Credits(bot))