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
7. You will respond to all other questions or comments with "INVALID_REQUEST" only.
8. You can edit the task log if the user asks you to do so.  You will respond with the same format as above, but with the changes made.
9. Use military time.
"""

class AiTimeActionLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.context = []
        self.system_prompt = SYSTEM_PROMPT
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.last_message = ""

    def get_full_context(self, scope):
        return self.context_header + self.contexts.get(scope, [])

    def rebuild_context(self, last_message):
        self.context = [
            {
                "role": "system", 
                "content": self.system_prompt
            },
            {
                "role": "user", 
                "content": "Here is the starting data:\n\n" + last_message
            },
            {
                "role": "assistant", 
                "content": last_message
            }
        ]

    async def process_action(self, data):
        if "TASK_COMPLETE" in data:
            self.context = []
            self.last_message = ""
            return 0
        
        if "INVALID_REQUEST" in data:
            return 0
        
        return 1

    async def parse_message(self, message):
        current_context = []
        if self.last_message:
            current_context = self.rebuild_context(self.last_message)
        else:
            current_context = self.context_header

        result = await omega.ai.chat_completion_context(
            self.model,
            current_context
        )

        self.last_message = result

        if self.process_action(result):
            await message.channel.send(result)

        return result

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != 1359963522368278679:
            return

        result = await self.parse_message(message.content)
        await self.process_action(result)

async def setup(bot: commands.Bot):
    await bot.add_cog(AiTimeActionLog(bot))