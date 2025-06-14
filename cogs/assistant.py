# cogs/assistant.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from datetime import datetime
from core.omega import omega

class Assistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.contexts = {}
        self.context_timestamps = {}
        self.system_prompt = "You are Omega, an AI assistant. Respond with short answers. If user input violates policy, reply with 'GIF:' and summarize the relevant words. This will help in finding related gifs for prohibited actions."
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.autorespond_channels = self.load_autorespond_channels()
        self.clear_inactive_contexts.start()
        self.rag_retrieval_entries = 3

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
            omega.logger.info(f"Cleared inactive context for {scope}")
            if scope.startswith("user_"):
                user_id = int(scope.split("_")[1])
                user = self.bot.get_user(user_id)
                if user:
                    await user.send(f"*Context cleared due to inactivity*", delete_after=5)
            if scope.startswith("channel_"):
                channel_id = int(scope.split("_")[1])
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(f"*Context cleared due to inactivity*", delete_after=5)

    @clear_inactive_contexts.before_loop
    async def before_clear_inactive_contexts(self):
        await self.bot.wait_until_ready()

    def save_autorespond_channels(self):
        with open("./config/autorespond_channels.json", "w") as file:
            json.dump(self.autorespond_channels, file)
            omega.logger.debug("Saved autorespond channels.")

    def load_autorespond_channels(self):
        try:
            with open("./config/autorespond_channels.json", "r") as file:
                omega.logger.debug("Loaded autorespond channels.")
                return json.load(file)
        except FileNotFoundError:
            omega.logger.warning("autorespond_channels.json not found. Returning empty list.")
            return []

    async def reply_to_message(self, message, prompt):
        ctx = await self.bot.get_context(message)
        async with ctx.typing():

            scope = self.get_scope(message)
            self.add_context(scope, 'user', prompt)

            rag_results = omega.rag.retrieve_context(prompt, self.rag_retrieval_entries)

            texts = [str(entry) for entry in rag_results]

            rag_info = "\n\nRelevant context:\n" + "\n".join(texts) if texts else ""
            dynamic_system_prompt = self.system_prompt + rag_info

            full_context = [{"role": "system", "content": dynamic_system_prompt}] + self.contexts.get(scope, [])

            result = omega.ai.chat_completion_context(self.model, full_context)
            
            usedagif = False
            if result.startswith("GIF:"):
                usedagif = True
                omega.logger.info("Circumvented annoying AI response by using a GIF. " + result)
                result = await omega.gfy.get_react_gif_url(result.replace("GIF:", ""))

            self.add_context(scope, 'assistant', result)

            tokens, cost, credits = omega.ai.update_cost(self.model, result, full_context, 0.15, 0.60)

            omega.ai.log_usage(message.author.id, tokens, cost, 'completion')

            if usedagif:
                await ctx.send(content=result)
                return

            footer = omega.ai.get_footer(tokens, cost)
            response_with_footer = result + footer

            if len(response_with_footer) > 4000:
                with open('file.txt', 'w') as f:
                    f.write(response_with_footer)
                file = discord.File('file.txt')
                await ctx.send(attachments=[file])
                omega.logger.debug("Response message exceeded 4000 characters, sent as a file.")
            elif len(response_with_footer) > 2000:
                embed = omega.embed.create_embed("", response_with_footer)
                await ctx.send(embed=embed)
                omega.logger.debug("Response message exceeded 2000 characters, sent as an embed.")
            else:
                await ctx.send(content=response_with_footer)



    @commands.Cog.listener()
    async def on_message(self, message):
        return
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
        if message.author.id == 198953041670569986 and len(message.content) > 350:
            result = omega.ai.chat_completion(
                self.model, 
                'You are an AI assistant named Omega, and your task is to summarize text.',
                'Please summarize the following as short as possible:\n\n' + message.content
            )
            channel = self.bot.get_channel(1232218996607287319)
            if channel:
                await channel.send('Looks like nicky made another wall of text.  Here is the summary:\n\n' + result)
            return
        # Strip bot tag
        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()

        # If we are in a dm, reply
        if isinstance(message.channel, discord.DMChannel):
            await self.reply_to_message(message, prompt)
            return

        # If we are not in a dm, check for bot tag or channel id in autorespond list
        id = message.channel.id
        if (
            isinstance(message.channel, discord.DMChannel)
            or self.bot.user.mentioned_in(message)
            or id in self.autorespond_channels
            or 'omega' in message.content.lower()
        ):
            await self.reply_to_message(message, prompt)

    @commands.has_permissions(manage_guild=True)
    @commands.command(name="addchannel")
    async def addchannel(self, context):
        return
        id = context.channel.id
        if id in self.autorespond_channels:
            await context.send("This channel is already added")
            omega.logger.info(f"Channel {id} is already in the autorespond list.")
        else:
            self.autorespond_channels.append(id)
            self.save_autorespond_channels()
            await context.send("Channel added")
            omega.logger.info(f"Added channel {id} to autorespond list.")
    
    @addchannel.error
    async def addchannel_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have the necessary permissions to use this command.")
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="removechannel")
    async def removechannel(self, context):
        return
        id = context.channel.id
        if id in self.autorespond_channels:
            self.autorespond_channels.remove(id)
            self.save_autorespond_channels()
            await context.send("Channel removed")
            omega.logger.info(f"Removed channel {id} from autorespond list.")
        else:
            await context.send("Channel was not in the list")
            omega.logger.info(f"Channel {id} was not in the autorespond list.")
    
    @removechannel.error
    async def removechannel_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have the necessary permissions to use this command.")
    
    @commands.command(name="usage")
    async def usage(self, context, user: discord.User = None):
        """
        Display usage and costs
        """
        userid = user.id if user else context.author.id
        user_id, tokens, completion_cost, dalle3_cost = omega.ai.get_usage(userid)
        total_cost = completion_cost + dalle3_cost
        if userid == user_id:
            desc=(
                "> 🪙 Tokens: %s\n"
                "> 📰 Completions: %s\n"
                "> 📷 Dalle-3: %s\n"
                "> 💰 Total Cost: %s\n\n"
            )
            desc_formatted = desc % (tokens, f"${completion_cost:.5f}".rstrip('0'), f"${dalle3_cost:.5f}".rstrip('0'), f"${total_cost:.5f}".rstrip('0'))
            embed = discord.Embed(
                title="Usage Information",
                description=desc_formatted,
                colour=omega.cfg.PRIMARYCOLOR,
                timestamp=datetime.now()
            )
            embed.set_author(name="Info",url="https://github.com/Clobie/omega",icon_url="https://github.com/Clobie/omega/blob/main/assets/omega.png?raw=true")
            embed.set_thumbnail(url="https://github.com/Clobie/omega/blob/main/assets/omega.png?raw=true")
            embed.set_footer(text="Omega",icon_url="https://github.com/Clobie/omega/blob/main/assets/omega.png?raw=true")
            await context.send(embed=embed)
        else:
            await context.send(f"👥 No usage data found for <@{user_id}>.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Assistant(bot))
