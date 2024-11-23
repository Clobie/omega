import os
import sys
import logging
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = self.bot.latency
        await ctx.send(f'Pong! Latency: {latency*1000:.2f} ms')
        logger.info(f'Responded to ping command with latency {latency*1000:.2f} ms')
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'Logged in as {self.bot.user}')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            logger.info(f'Command not found: {ctx.message.content}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument.')
            logger.info(f'Missing required argument in command: {ctx.message.content}')
        else:
            await ctx.send(f'An error occurred: {str(error)}')
            logger.error(f'An error occurred: {str(error)}')
            raise error
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        server_name = ctx.guild.name.encode('unicode_escape').decode('utf-8')
        channel_name = ctx.channel.name.encode('unicode_escape').decode('utf-8')
        command_content = ctx.message.content.encode('unicode_escape').decode('utf-8')
        channel_id = ctx.channel.id
        logger.info(f"Command '{command_content}' entered by {ctx.author} in {server_name} ({channel_name}) [channel id: {channel_id}]")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        server_name = ctx.guild.name.encode('unicode_escape').decode('utf-8')
        channel_name = ctx.channel.name.encode('unicode_escape').decode('utf-8')
        command_content = ctx.message.content.encode('unicode_escape').decode('utf-8')
        channel_id = ctx.channel.id
        logger.info(f"Command '{command_content}' completed by {ctx.author} in {server_name} ({channel_name}) [channel id: {channel_id}]")

    @commands.Cog.listener()
    async def on_message(self, message):
        server_name = message.guild.name.encode('unicode_escape').decode('utf-8')
        channel_name = message.channel.name.encode('unicode_escape').decode('utf-8')
        command_content = message.content.encode('unicode_escape').decode('utf-8')
        channel_id = message.channel.id
        logger.info(f"Message from {message.author} in {server_name} ({channel_name}) [channel id: {channel_id}]: {command_content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        server_name = before.guild.name.encode('unicode_escape').decode('utf-8')
        channel_name = before.channel.name.encode('unicode_escape').decode('utf-8')
        before_content = before.content.encode('unicode_escape').decode('utf-8')
        after_content = after.content.encode('unicode_escape').decode('utf-8')
        channel_id = before.channel.id
        logger.info(f"Message edited by {before.author} in {server_name} ({channel_name}) [channel id: {channel_id}]:"
            f"\nBefore: {before_content}"
            f"\nAfter: {after_content}")

async def setup(bot):
    await bot.add_cog(General(bot))