import logging
import asyncio
from collections import deque
from datetime import datetime, timedelta

class DiscordLogHandler(logging.Handler):
	def __init__(self, bot, channel_id, level=logging.DEBUG, flush_interval=5, batch_size=10):
		super().__init__(level)
		self.bot = bot
		self.channel_id = channel_id
		self.flush_interval = flush_interval
		self.batch_size = batch_size
		self.queue = deque()
		self._last_flush = datetime.now()
		self._flush_task = bot.loop.create_task(self._flush_logs_periodically())

	async def _flush_logs_periodically(self):
		await self.bot.wait_until_ready()
		while True:
			await asyncio.sleep(self.flush_interval)
			await self._flush()

	async def _flush(self):
		if not self.queue:
			return

		channel = self.bot.get_channel(self.channel_id)
		if not channel:
			return

		messages = []
		while self.queue and len(messages) < self.batch_size:
			messages.append(self.queue.popleft())

		log_message = "\n".join(f"[Log] {msg}" for msg in messages)

		for chunk in self._chunk_message(log_message):
			await channel.send(f"```{chunk}```")

	def _chunk_message(self, message, limit=1900):
		lines = message.split("\n")
		chunks = []
		current_chunk = ""

		for line in lines:
			if len(current_chunk) + len(line) + 1 > limit:
				chunks.append(current_chunk)
				current_chunk = line
			else:
				if current_chunk:
					current_chunk += "\n"
				current_chunk += line

		if current_chunk:
			chunks.append(current_chunk)

		return chunks

	def emit(self, record):
		log_entry = self.format(record)
		self.queue.append(log_entry)
