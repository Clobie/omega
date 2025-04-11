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

class AiTimeActionLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = 'gpt-4o-mini'
        self.thinking_emoji = "<a:ai_thinking:1309172561250353224>"
        self.system_prompt = SYSTEM_PROMPT
        self.context_header = [{"role": "system", "content": self.system_prompt}]
        self.last_message = ""
        self.context = []

    def get_full_context(self, scope):
        context = self.context_header + self.contexts.get(scope, [])
        omega.logger.info(f"Retrieved full context for scope '{scope}': {context}")
        return context

    def append_context(self, scope, message):
        if scope not in self.contexts:
            omega.logger.warning(f"Scope '{scope}' not found.")
        else:
            self.context.append(
                {
                    "role": scope,
                    "content": message
                }
            )
            omega.logger.info(f"Appended message to context for scope '{scope}': {message}")

    def rebuild_context(self, new_message):
        omega.logger.info("Rebuilding context with last_message.")

        if self.last_message:
            rebuilt = [
                {
                    "role": "system", 
                    "content": self.system_prompt
                },
                {
                    "role": "user", 
                    "content": "Here is the starting data:\n\n" + self.last_message
                },
                {
                    "role": "assistant", 
                    "content": self.last_message
                },
                {
                    "role": "user", 
                    "content": new_message
                },
            ]
        else:
            rebuilt = [
                {
                    "role": "system", 
                    "content": self.system_prompt
                },
                {
                    "role": "user", 
                    "content": new_message
                },
            ]
        omega.logger.debug(f"Rebuilt context: {rebuilt}")
        self.context = rebuilt
        return rebuilt

    async def process_action(self, data):
        omega.logger.info("Processing action with data: " + data)
        if "TASK_COMPLETE" in data:
            omega.logger.info("Detected TASK_COMPLETE in data. Clearing context and last_message.")
            self.context = []
            self.last_message = ""
            omega.logger.debug("Context and last_message cleared.")
            return False

        if "INVALID_REQUEST" in data:
            omega.logger.info("Detected INVALID_REQUEST in data. No further processing.")
            return False
        
        if "TASKLOG" in data:
            omega.logger.info("Detected TASKLOG in data. Processing task log.")
            self.rebuild_context(data)
            return True

        return True

    async def parse_message(self, message):
        omega.logger.info("Parsing new message.")

        if not self.last_message:
            self.rebuild_context(message.content)

        result = "asdf"

        try:
            result = omega.ai.chat_completion_context(
                self.model,
                self.context
            )
        except Exception as e:
            omega.logger.error(f"Error during chat_completion_context: {e}")
            return "INVALID_REQUEST"

        self.last_message = result
        self.append_context("assistant", result)
        omega.logger.debug(f"Updated last_message: {self.last_message}")

        process_result = await self.process_action(result)
        if process_result:
            omega.logger.info("Sending result message to channel.")
            await message.channel.send(result)
        else:
            omega.logger.info("Result did not require sending a message.")

        return result

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            omega.logger.debug("Message from bot ignored.")
            return

        if message.channel.id != 1359963522368278679:
            omega.logger.debug(f"Message from channel {message.channel.id} ignored.")
            return

        omega.logger.info(f"New message received from user {message.author.id} in allowed channel.")
        result = await self.parse_message(message)
        await self.process_action(result)

async def setup(bot: commands.Bot):
    await bot.add_cog(AiTimeActionLog(bot))
