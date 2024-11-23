# cogs/assistant.py

import discord
from discord.ext import commands
import logging
import utils.config
import utils.ai as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Assistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')
        self.context = []
        self.system_prompt = "You are a helpful AI assistant named Jenkins.  Use short and concise responses."
        self.context_header = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

    def clear_context(self):
        self.context = []
    
    def add_context(self, scope, content):
        if scope == 'user':
            self.context.append(
                {
                    "role": "user",
                    "content": content
                }
            )
        if scope == 'assistant':
            self.context.append(
                {
                    "role": "assistant",
                    "content": content
                }
            )
    
    def get_full_context(self):
        context = self.context_header
        context.append(self.context)
        return context

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "clear context":
            self.clear_context()
            await message.add_reaction("✅")
            return
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        self.add_context('user', prompt)
        result = self.ai.chat_completion_context('gpt-4o-mini', self.context)
        self.add_context('assistant', result)
        await message.reply(result)


async def setup(bot: commands.Bot):
    await bot.add_cog(Assistant(bot))