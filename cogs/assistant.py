# cogs/assistant.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from utils.ai import ai
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.giphy import gfy
from utils.credit import credit

class Assistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.contexts = {}
        self.context_timestamps = {}
        self.system_prompt = "You are Omega, an AI assistant. Respond with short answers. If user input violates policy, reply with 'GIF:' and summarize the relevant words. This will help in finding related gifs for prohibited actions."
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.autorespond_channels = self.load_autorespond_channels()
        self.clear_inactive_contexts.start()

    def get_scope(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return f"user_{message.author.id}"
        else:
            return f"channel_{message.channel.id}"

    def clear_context(self, scope):
        if scope in self.contexts:
            del self.contexts[scope]
            del self.context_timestamps[scope]

    def add_context(self, scope, role, content):
        if scope not in self.contexts:
            self.contexts[scope] = []
        self.contexts[scope].append({"role": role, "content": content})
        self.context_timestamps[scope] = time.time()

    def get_full_context(self, scope):
        return self.context_header + self.contexts.get(scope, [])

    @tasks.loop(seconds=60)
    async def clear_inactive_contexts(self):
        current_time = time.time()
        to_clear = [scope for scope, last_used in self.context_timestamps.items() if current_time - last_used > 300]
        for scope in to_clear:
            self.clear_context(scope)
            logger.info(f"Cleared inactive context for {scope}")

    @clear_inactive_contexts.before_loop
    async def before_clear_inactive_contexts(self):
        await self.bot.wait_until_ready()

    def save_autorespond_channels(self):
        with open("./config/autorespond_channels.json", "w") as file:
            json.dump(self.autorespond_channels, file)
            logger.debug("Saved autorespond channels.")

    def load_autorespond_channels(self):
        try:
            with open("./config/autorespond_channels.json", "r") as file:
                logger.debug("Loaded autorespond channels.")
                return json.load(file)
        except FileNotFoundError:
            logger.warning("autorespond_channels.json not found. Returning empty list.")
            return []

    async def reply_to_message(self, message, prompt):
        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            scope = self.get_scope(message)
            self.add_context(scope, 'user', prompt)

            # Calculate token estimate for context
            full_context = self.get_full_context(scope)

            # Get AI response
            result = ai.chat_completion_context(self.model, full_context)
            
            usedagif = False
            if result.startswith("GIF:"):
                usedagif = True
                logger.info("Circumvented annoying AI response by using a GIF. " + result)
                result = await gfy.get_react_gif_url(result.replace("GIF:", ""))

            # Add response to context
            self.add_context(scope, 'assistant', result)

            # Get tokens, cost
            tokens, cost, credits = ai.update_cost(self.model, result, full_context, 0.15, 0.60) # magic numbers bad
            
            credit.user_spend(message.author.id, credits)

            if usedagif:
                await ctx.send(content=result)
                return

            # Get footer
            footer = ai.get_footer(tokens, cost)

            # Build full message
            response_with_footer = result + footer

            await status.update(self.bot, 'watching', f"Cost: ${ai.get_total_cost()}")

            # Reply with file/embed/text based on response length (because of discord limits)
            if len(response_with_footer) > 4000:
                with open('file.txt', 'w') as f:
                    f.write(response_with_footer)
                file = discord.File('file.txt')
                await ctx.send(attachments=[file])
                logger.debug("Response message exceeded 4000 characters, sent as a file.")
            elif len(response_with_footer) > 2000:
                embed = discord.Embed(description=response_with_footer)
                await ctx.send(embed=embed)
                logger.debug("Response message exceeded 2000 characters, sent as an embed.")
            else:
                await ctx.send(content=response_with_footer)


    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignore other bots
        if message.author.bot:
            return
        
        # Ignore if a command was sent
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        
        # Clear context and ignore if clear context was sent
        if message.content == "clear context":
            scope = self.get_scope(message)
            self.clear_context(scope)
            await message.add_reaction("✅")
            return

        # Strip bot tag
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()

        # If we are in a dm, reply
        if isinstance(message.channel, discord.DMChannel):
            await self.reply_to_message(message, prompt)
            return

        # If we are not in a dm, check for bot tag or channel id in autorespond list
        id = message.channel.id
        if not self.bot.user.mentioned_in(message) and id not in self.autorespond_channels:
            return

        # Reply
        await self.reply_to_message(message, prompt)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="addchannel")
    async def addchannel(self, context):
        id = context.channel.id
        if id in self.autorespond_channels:
            await context.send("This channel is already added")
            logger.info(f"Channel {id} is already in the autorespond list.")
        else:
            self.autorespond_channels.append(id)
            self.save_autorespond_channels()
            await context.send("Channel added")
            logger.info(f"Added channel {id} to autorespond list.")
    
    @addchannel.error
    async def addchannel_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have the necessary permissions to use this command.")
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="removechannel")
    async def removechannel(self, context):
        id = context.channel.id
        if id in self.autorespond_channels:
            self.autorespond_channels.remove(id)
            self.save_autorespond_channels()
            await context.send("Channel removed")
            logger.info(f"Removed channel {id} from autorespond list.")
        else:
            await context.send("Channel was not in the list")
            logger.info(f"Channel {id} was not in the autorespond list.")
    
    @removechannel.error
    async def removechannel_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have the necessary permissions to use this command.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Assistant(bot))
