# cogs/ai_time_task_log.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from datetime import datetime
from core.omega import omega

SYSTEM_PROMPT = """
You are an AI assistant and your purpose is to log tasks and what time they occurred.

The following is your ruleset:

1. If there is no existing log, politely explain what your role is and ask if they would like to start a new log.  If they say yes, ask for the date.
2. User may add tasks and times.  You will remember these for the TASKLOG section.
3. User may add notes that are not specific to a task entry.  You can remember these for the NOTES section.
4. Once you have both the time and task, you will respond ONLY with the complete list of times and accompanying tasks in the following format, with no other text:
5. If multiple notes are given at once, put them on separate lines in the NOTES section.
6. If the user says and variant of "i am done", "I am finished", "clear context", "delete data" or similar, you will respond with the full log in the following format, followed by "END_TASKLOG" at the end.

```
DATE
date_here

TASKLOG
TIME | TASK (repeat for each task)

NOTES
notes_here
```

"""

class AiTimeTaskLog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.contexts = {}
        self.context_timestamps = {}
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
            response_with_footer = (result + footer).replace("END_TASKLOG", "")

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

        if "END_TASKLOG" in result:
            self.clear_context(scope)

        if "TASKLOG" in result and "DATE" in result and "NOTES" in result:
            self.clear_context(scope)
            self.add_context(scope, 'user', "current log to start from: \n" + result)
            self.add_context(scope, 'assistant', result)

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
