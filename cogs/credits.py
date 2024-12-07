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
            omega.logger.info(query_server % guild.id)
            omega.db.run_script(query_server, (guild.id,))
            
            for member in guild.members:
                query_user = (
                    "INSERT INTO discord_users (user_id, credits) "
                    "VALUES (%s, 0) "
                    "ON CONFLICT (user_id) DO NOTHING"
                )
                omega.logger.info(query_user % member.id)
                omega.db.run_script(query_user, (member.id,))
    
    def get_credits(self, user_id):
        query = (
            "WITH upsert AS ("
            "    INSERT INTO discord_users (user_id, credits) "
            "    VALUES (%s, 0) "
            "    ON CONFLICT (user_id) DO NOTHING "
            ") "
            "SELECT credits FROM discord_users WHERE user_id = %s;"
        )
        result = omega.db.run_script(query, (user_id, user_id))
        return result
    
    def give_credits(self, user_from, user_to, amount):
        if amount <= 0:
            return False
        from_credits = self.get_credits(user_from)
        to_credits = self.get_credits(user_to)

        if from_credits is None or to_credits is None:
            return False  # At least one user doesn't exist
        
        # Check if user_from has enough credits
        if from_credits < amount:
            return False

        # Execute the credit transfer
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
        
        omega.db.run_script(query, (amount, user_from, amount, user_to))
        return True

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

async def setup(bot: commands.Bot):
    await bot.add_cog(Credits(bot))