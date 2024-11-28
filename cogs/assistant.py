# cogs/assistant.py

import discord
from discord.ext import commands, tasks
import logging
import json
import time
import utils.config
import utils.ai as ai
import tiktoken  # Install with `pip install tiktoken`

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Assistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = ai.instantiate()
        self.cfg = utils.config.instantiate('./config/bot.conf')
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.contexts = {}  # Stores contexts by scope (user or channel)
        self.context_timestamps = {}  # Tracks last activity for each scope
        self.system_prompt = "You are a helpful AI assistant named Omega. Use short and concise responses."
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.autorespond_channels = self.load_autorespond_channels()
        self.clear_inactive_contexts.start()  # Start the cleanup task
        self.total_cost = self.load_cost_from_file()
    
    def load_cost_from_file(self):
        """Load accumulated cost from a file."""
        try:
            with open("./config/cost_data.json", "r") as file:
                cost_data = json.load(file)
                return cost_data.get("total_cost", 0.0)
        except FileNotFoundError:
            logging.warning("cost_data.json not found. Starting with a cost of 0.")
            return 0.0

    async def update_status(self):
        """Update the bot's status to show the accumulated cost and save it to file."""
        cost_display = f"Accumulated Cost: ${self.total_cost:.6f}"
        await self.bot.change_presence(activity=discord.Game(name=cost_display))
        self.save_cost_to_file()

    def save_cost_to_file(self):
        """Save the accumulated cost to a file."""
        cost_data = {"total_cost": self.total_cost}
        with open("./config/cost_data.json", "w") as file:
            json.dump(cost_data, file, indent=4)
        logging.debug("Saved accumulated cost to file.")



    def get_scope(self, message):
        """Determine the scope based on the message."""
        if isinstance(message.channel, discord.DMChannel):
            return f"user_{message.author.id}"
        else:
            return f"channel_{message.channel.id}"

    def clear_context(self, scope):
        """Clear context for a specific scope."""
        if scope in self.contexts:
            del self.contexts[scope]
            del self.context_timestamps[scope]

    def add_context(self, scope, role, content):
        """Add context to the specific scope."""
        if scope not in self.contexts:
            self.contexts[scope] = []
        self.contexts[scope].append({"role": role, "content": content})
        self.context_timestamps[scope] = time.time()  # Update the last activity time

    def get_full_context(self, scope):
        """Get the full context for a specific scope."""
        return self.context_header + self.contexts.get(scope, [])

    @tasks.loop(seconds=60)
    async def clear_inactive_contexts(self):
        """Clear contexts that haven't been used in 5 minutes."""
        current_time = time.time()
        to_clear = [scope for scope, last_used in self.context_timestamps.items() if current_time - last_used > 300]
        for scope in to_clear:
            self.clear_context(scope)
            logging.info(f"Cleared inactive context for {scope}")

    @clear_inactive_contexts.before_loop
    async def before_clear_inactive_contexts(self):
        await self.bot.wait_until_ready()

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

    def estimate_tokens(self, text):
        """Estimate the number of tokens used in a given text."""
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))

    def to_superscript(self, text):
        # Mapping numbers and lowercase letters to superscript characters
        superscript_mapping = str.maketrans(
            "0123456789abcdefghijklmnopqrstuvwxyz.-",
            "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ˙ˉ"
        )
        return text.translate(superscript_mapping)

    async def reply_to_message(self, message, prompt):
        ctx = await self.bot.get_context(message)
        #reply_msg = await message.channel.send(self.thinking_emoji)
        async with ctx.typing():
            scope = self.get_scope(message)
            self.add_context(scope, 'user', prompt)

            # Calculate token estimate for context
            full_context = self.get_full_context(scope)
            context_text = "\n".join([f"{entry['role']}: {entry['content']}" for entry in full_context])
            context_tokens = self.estimate_tokens(context_text)

            # Get AI response
            result = self.ai.chat_completion_context(self.model, full_context)
            self.add_context(scope, 'assistant', result)

            # Calculate token estimate for the result
            result_tokens = self.estimate_tokens(result)
            total_tokens = context_tokens + result_tokens

            # Calculate cost estimate
            cost_per_million_input = 0.15  # Cost in dollars per million input tokens
            cost_per_million_output = 0.60  # Cost in dollars per million output tokens
            cost_estimate = ((context_tokens / 1_000_000) * cost_per_million_input) + \
                            ((result_tokens / 1_000_000) * cost_per_million_output)
            
            self.total_cost += cost_estimate  # Accumulate cost
            await self.update_status()

            # Append token estimate and cost to the response
            #footer = (
            #    f"\n\n*Token estimate: Context={context_tokens}, Response={result_tokens}, "
            #    f"Total={total_tokens}, Cost=${cost_estimate:.6f}*"
            #)
            text = self.to_superscript(f"{total_tokens}tk - cost{cost_estimate:.6f}")
            footer = (
                f"\n\n*{text}*"
            )

            # Handle message response
            response_with_footer = result + footer
            if len(response_with_footer) > 4000:
                with open('file.txt', 'w') as f:
                    f.write(response_with_footer)
                file = discord.File('file.txt')
                await ctx.send(attachments=[file])
                logging.debug("Response message exceeded 4000 characters, sent as a file.")
            elif len(response_with_footer) > 2000:
                embed = discord.Embed(description=response_with_footer)
                await ctx.send(embed=embed)
                logging.debug("Response message exceeded 2000 characters, sent as an embed.")
            else:
                await ctx.send(content=response_with_footer)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        
        if message.content == "clear context":
            scope = self.get_scope(message)
            self.clear_context(scope)
            await message.add_reaction("✅")
            return

        prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()

        if isinstance(message.channel, discord.DMChannel):
            await self.reply_to_message(message, prompt)
            return

        id = message.channel.id
        if not self.bot.user.mentioned_in(message) and id not in self.autorespond_channels:
            return

        await self.reply_to_message(message, prompt)

async def setup(bot: commands.Bot):
    await bot.add_cog(Assistant(bot))
