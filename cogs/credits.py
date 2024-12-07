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
        for guild in self.bot.guilds:
            query_server = (
                "INSERT INTO discord_servers (server_id, credits) "
                "VALUES (%s, 0) "
                "ON CONFLICT (server_id) DO NOTHING"
            )
            formatted_server_query = query_server % guild.id
            omega.logger.info(formatted_server_query)
            omega.db.run_script(formatted_server_query)
            
            for member in guild.members:
                query_user = (
                    "INSERT INTO discord_users (user_id, credits) "
                    "VALUES (%s, 0) "
                    "ON CONFLICT (user_id) DO NOTHING"
                )
                formatted_user_query = query_user % member.id
                omega.logger.info(formatted_user_query)
                omega.db.run_script(formatted_user_query)
    
    def get_credits(self, user_id):
        query = (
            "SELECT credits FROM discord_users WHERE user_id = %s;"
        )
        formatted_query = query % (user_id)
        result = omega.db.run_script(formatted_query)
        return result[0][0] if result else None
    
    def give_credits(self, user_from, user_to, amount):
        if amount <= 0:
            return False
        from_credits = self.get_credits(user_from)
        to_credits = self.get_credits(user_to)

        if from_credits is None or to_credits is None:
            return False
        
        if from_credits < amount:
            return False

        query = (
            "WITH deducted AS ("
            "    UPDATE discord_users "
            "    SET credits = credits - %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            "), "
            "added AS ("
            "    UPDATE discord_users "
            "    SET credits = credits + %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            ") "
            "SELECT (SELECT credits FROM deducted) AS from_credits, "
            "       (SELECT credits FROM added) AS to_credits;"
        )
        formatted_query = query % ((amount, user_from, amount, user_to))
        omega.db.run_script(formatted_query)
        return True
    
    def gift_credits(self, user_to, amount):
        if amount <= 0:
            return False
        to_credits = self.get_credits(user_to)
        if to_credits is None:
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits + %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, user_to)
        new_credits = omega.db.run_script(formatted_query)
        return new_credits is not None
    
    def take_credits(self, user_from, amount):
        if amount <= 0:
            return False
        from_credits = self.get_credits(user_from)
        if from_credits is None or from_credits < amount:
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits - %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, user_from)
        new_credits = omega.db.run_script(formatted_query)
        return new_credits is not None

    @commands.command(name='credits')
    async def credits(self, ctx):
        credits = self.get_credits(ctx.author.id)
        await ctx.send(f"You have {credits} credits.")

    @commands.command(name='give')
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to give.")
            return
        user_from_id = ctx.author.id
        user_to_id = member.id
        if self.give_credits(user_from_id, user_to_id, amount):
            await ctx.send(f"You've given {amount} credits to {member.mention}.")
        else:
            await ctx.send("You don't have enough credits.")
    
    @commands.command(name='gift')
    async def gift(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to give.")
            return
        if self.gift_credits(member.id, amount):
            await ctx.send(f"You've given {amount} credits to {member.mention}.")
    
    @commands.command(name='take')
    async def take(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("Specify a valid amount of credits to take.")
            return
        if self.take_credits(member.id, amount):
            await ctx.send(f"You've taken {amount} credits from {member.mention}.")
        else:
            await ctx.send(f"Failed to take credits from {member.mention}. They may not have enough credits.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Credits(bot))