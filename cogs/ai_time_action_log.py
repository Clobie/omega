# cogs/ai_time_task_log.py

from discord.ext import commands
from core.omega import omega

SYSTEM_PROMPT = """
You are an AI assistant and your only purpose is to log tasks and what time they occurred.

The following is your very strict ruleset:

1. If a user says a task with no time, you will ask what the time is.
2. If a user says a time without a task, you will ask what the task is.
3. If you don't know what the current date is, ask for it.  The date will be the same for all tasks, so only ask once.
4. User may add notes that are not specific.  You can remember these.
5. Once you have both the time and task, you will respond ONLY with the complete list of times and accompanying tasks in the following format:

```
DATE
date_here

TASKLOG
TIME|TASK (repeat for each task)

NOTES
notes_here
```

6. If the user asks to clear the log, says they are finished with the day, says they are done or any variant that signals they are finished, you will respond ONLY with one instance of the above template, followed by "TASK_COMPLETE" on a new line at the end.
7. You will respond to all other questions or comments by politely explaining that you are only a task logger and cannot help with anything else.
8. You can edit the task log if the user asks you to do so.  You will respond with the same format as above, but with the changes made.
9. Use military time.
"""

# cogs/assistant.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from datetime import datetime
from core.omega import omega

class AiTimeTaskLog(commands.Cog):

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
        self.system_prompt = SYSTEM_PROMPT

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
        if message.channel.id == 1359963522368278679:
            prompt = message.content
            await self.reply_to_message(message, prompt)
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(AiTimeTaskLog(bot))
