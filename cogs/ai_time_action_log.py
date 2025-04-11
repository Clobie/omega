# cogs/ai_time_task_log.py

from discord.ext import commands
from core.omega import omega

SYSTEM_PROMPT = """
You are an AI assistant and your only purpose is to log tasks and what time they occurred.

The following is your very strict ruleset:

1. If there is no existing log, politely explain what your role is and ask the user the provide today's date.
2. If there is an existing log, ask the user if they would like to add to it, edit it, or clear it.
3. User may add tasks and times.  You will remember these.  If either time or task data is missing, you will ask for it.
4. User may add notes that are not specific to a task entry.  You can remember these for the NOTES section.
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
7. Use military time. eg. 14:00 instead of 2:00 pm.
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

    async def reply_to_message(self, message, prompt):
        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            scope = self.get_scope(message)
            self.add_context(scope, 'user', prompt)
            full_context = self.get_full_context(scope)
            result = omega.ai.chat_completion_context(self.model, full_context)
            self.add_context(scope, 'assistant', result)
            tokens, cost, credits = omega.ai.update_cost(self.model, result, full_context, 0.15, 0.60)
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
