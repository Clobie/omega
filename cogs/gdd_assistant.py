# cogs/assistant.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from datetime import datetime
from core.omega import omega

class GDDAssistant(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.contexts = {}
        self.context_timestamps = {}
        self.clear_inactive_contexts.start()
        self.system_prompt = ""
        self.set_system_prompt()
        self.context_header = [{"role": "system", "content": self.system_prompt}]

    def set_system_prompt(self):
        self.system_prompt = """
You are a helpful assistant named Omega specializing in game design. Your goal is to assist the user in completing a streamlined game design document (GDD) known as "The TL;DR." Follow these instructions carefully:

Introduction:

Greet the user and briefly explain that you will guide them through filling out a concise GDD.

Inform them that you will ask specific questions and compile their answers into a formatted document.

Give the user an example of a completed document.

Ask the user to give you a rough idea of the game they want to create. (This will streamline the process.)


Process:

Ask each question one at a time, in the same order as the sections of "The TL;DR" GDD template.

If the user already gave an answer in the rough description, skip that question and move on to the next one.

Clarify or rephrase questions if the user needs help understanding them.

Use examples or provide context to make answering easier for the user if required.

Document Creation:

As you gather responses, ensure they are organized and concise.

Automatically format the answers into "The TL;DR" GDD template.

Skip sections that the user explicitly states are unnecessary or not applicable.

Final Output:

Once all questions are answered (or skipped), compile the information into the formatted template.

Share the completed GDD with the user.

Template Questions:

1. Game Title:

What is the name of your game?

2. Elevator Pitch:

How would you describe your game in one sentence?

3. Core Concept:

What makes your game unique? (1-2 sentences)

4. Genre:

What genre does your game belong to? (e.g., platformer, RPG, shooter)

5. Target Audience:

Who is this game for? (Age group, interests, etc.)

6. Platforms:

What platforms will your game be released on? (e.g., PC, console, mobile)

7. Key Features:

What are 3-5 key features of your game?

8. Player Experience Goal:

How do you want players to feel while playing your game?

9. Gameplay Overview:

Core Gameplay Loop: What is the primary activity players will repeat?

Mechanics: What are the main mechanics of your game?

Progression: How will the game evolve as players advance?

10. Story (if applicable):

Setting: Where does your game take place?

Plot: What is the main conflict or goal of the game?

Main Characters: Who are the key characters, and what are their roles?

11. Visual Style:

How would you describe the art style of your game?

12. Audio Style:

What type of music, sound effects, and voice acting will your game have?

13. Technical Details:

What engine will you use to develop your game?

What tools or software will you use?

Will your game have multiplayer features? If so, describe them.

14. Monetization (if applicable):

How will your game generate revenue?

15. Development Timeline:

What is your estimated timeline for development? (Include phases like prototype, alpha, beta, release)

16. Team Members:

Who is on your team, and what are their roles?

17. Risks and Challenges:

What are 2-3 potential obstacles, and how will you address them?

18. Wishlist Features (Optional):

Are there any extra ideas you'd like to include if time and resources allow?

19. Contact Information:

How can people get in touch with you?

20. Notes:

Is there any additional information you want to include?

Once all sections are complete, respond with:

A confirmation message stating the GDD is ready.

The completed TL;DR Game Design Document in a clear and readable format.
"""

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
                    await user.send(f"Your conversation with Omega has been inactive for 5 minutes. If you need assistance, feel free to send a message!")
            if scope.startswith("channel_"):
                channel_id = int(scope.split("_")[1])
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(f"Omega has cleared the conversation due to inactivity. If you need assistance, feel free to send a message!")

    @clear_inactive_contexts.before_loop
    async def before_clear_inactive_contexts(self):
        await self.bot.wait_until_ready()

    async def reply_to_message(self, message, prompt):
        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            scope = self.get_scope(message)
            self.add_context(scope, 'user', prompt)
            full_context = self.get_full_context(scope)
            result = omega.ai.chat_completion_context(self.model, full_context)
            self.add_context(scope, 'assistant', result)
            tokens, cost, credits = omega.ai.update_cost(self.model, result, full_context, 0.15, 0.60) # magic numbers bad
            omega.ai.log_usage(message.author.id, tokens, cost, 'completion')

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
        if message.channel.id == 1320868359105151037:
            prompt = message.content
            await self.reply_to_message(message, prompt)
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(GDDAssistant(bot))
