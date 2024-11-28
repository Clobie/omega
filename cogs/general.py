# cogs/general.py

import logging
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        server_name = getattr(ctx.guild, 'name', 'DM')
        channel_name = getattr(ctx.channel, 'name', 'Direct Message')
        command_content = ctx.message.content.encode('unicode_escape').decode('utf-8')
        channel_id = ctx.channel.id
        
        user_info = f"{ctx.author.name} (ID: {ctx.author.id})" if ctx.guild else f"{ctx.author.name} (ID: {ctx.author.id})"
        logger.info(f"Command '{command_content}' entered by {user_info} in {server_name} ({channel_name}) [channel id: {channel_id}]")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        server_name = getattr(ctx.guild, 'name', 'DM')
        channel_name = getattr(ctx.channel, 'name', 'Direct Message')
        command_content = ctx.message.content.encode('unicode_escape').decode('utf-8')
        channel_id = ctx.channel.id

        user_info = f"{ctx.author.name} (ID: {ctx.author.id})"
        logger.info(f"Command '{command_content}' completed by {user_info} in {server_name} ({channel_name}) [channel id: {channel_id}]")

    @commands.Cog.listener()
    async def on_message(self, message):
        server_name = getattr(message.guild, 'name', 'DM')
        channel_name = getattr(message.channel, 'name', 'Direct Message')
        command_content = message.content.encode('unicode_escape').decode('utf-8')
        channel_id = message.channel.id

        user_info = f"{message.author.name} (ID: {message.author.id})"
        logger.info(f"Message from {user_info} in {server_name} ({channel_name}) [channel id: {channel_id}]: {command_content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        server_name = getattr(before.guild, 'name', 'DM')
        channel_name = getattr(before.channel, 'name', 'Direct Message')
        before_content = before.content.encode('unicode_escape').decode('utf-8')
        after_content = after.content.encode('unicode_escape').decode('utf-8')
        channel_id = before.channel.id

        user_info = f"{before.author.name} (ID: {before.author.id})"
        logger.info(f"Message edited by {user_info} in {server_name} ({channel_name}) [channel id: {channel_id}]:"
            f"\nBefore: {before_content}"
            f"\nAfter: {after_content}")

async def setup(bot):
    await bot.add_cog(General(bot))