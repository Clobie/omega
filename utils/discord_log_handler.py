import logging
import asyncio

class DiscordLogHandler(logging.Handler):
	def __init__(self, bot, channel_id, level=logging.NOTSET):
		super().__init__(level)
		self.bot = bot
		self.channel_id = channel_id

	async def _send_log(self, message):
		await self.bot.wait_until_ready()
		channel = self.bot.get_channel(self.channel_id)
		if channel:
			await channel.send(f'`[Log]` {message}')

	def emit(self, record):
		log_entry = self.format(record)
		asyncio.create_task(self._send_log(log_entry))
	