# cogs/assistant.py

import discord
from discord.ext import commands
import logging
import json
import utils.config
import utils.ai as ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Assistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.context = []
        self.system_prompt = "You are a helpful AI assistant named Jenkins.  Use short and concise responses."
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.autorespond_channels = self.load_autorespond_channels()

    def clear_context(self):
        self.context = []
    
    def add_context(self, scope, content):
        if scope == 'user':
            self.context.append({"role": "user","content": content})
        if scope == 'assistant':
            self.context.append({"role": "assistant","content": content})
    
    def get_full_context(self):
        return self.context_header + self.context

    def save_autorespond_channels(self):
        """Save autorespond channels to file."""
        with open("./config/autorespond_channels.json", "w") as file:
            json.dump(self.autorespond_channels, file)
            logging.debug("Saved autorespond channels.")

    def load_autorespond_channels(self):
        """Load autorespond channels from file."""
        try:
            with open("./config/autorespond_channels.json", "r") as file:
                logging.debug("Loaded autorespond channels.")
                return json.load(file)
        except FileNotFoundError:
            logging.warning("autorespond_channels.json not found. Returning empty list.")
            return []
    
    @commands.command(name="addchannel")
    async def addchannel(self, context):
        id = context.channel.id
        if id in self.autorespond_channels:
            await context.send("This channel is already added")
            logging.info(f"Channel {id} is already in the autorespond list.")
        else:
            self.autorespond_channels.append(id)
            self.save_autorespond_channels()
            await context.send("Channel added")
            logging.info(f"Added channel {id} to autorespond list.")
    
    @commands.command(name="removechannel")
    async def removechannel(self, context):
        id = context.channel.id
        if id in self.autorespond_channels:
            self.autorespond_channels.remove(id)
            self.save_autorespond_channels()
            await context.send("Channel removed")
            logging.info(f"Removed channel {id} from autorespond list.")
        else:
            await context.send("Channel was not in the list")
            logging.info(f"Channel {id} was not in the autorespond list.")

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
        id = message.channel.id
        if (not self.bot.user.mentioned_in(message) and id not in self.autorespond_channels):
            return
        reply_msg = await ctx.send(self.thinking_emoji)
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
        self.add_context('user', prompt)
        result = self.ai.chat_completion_context(self.model, self.get_full_context())
        self.add_context('assistant', result)
        if len(result) > 4000:
            with open('file.txt', 'w') as f:
                f.write(result)
            file = discord.File('file.txt')
            await reply_msg.edit(attachments=[file])
            logging.debug("Response message exceeded 4000 characters, sent as a file.")
        elif len(result) > 2000:
            embed = discord.Embed(description=result)
            await reply_msg.edit(embed=embed, attachments=[])
            logging.debug("Response message exceeded 2000 characters, sent as an embed.")
        else:
            await reply_msg.edit(content=result, attachments=[])

async def setup(bot: commands.Bot):
    await bot.add_cog(Assistant(bot))