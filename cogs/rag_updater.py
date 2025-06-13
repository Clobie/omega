import discord
import asyncio
import aiohttp
from discord.ext import commands, tasks
from core.omega import omega
from datetime import datetime
import pytz

class RagUpdater(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.weather_doc_id = "weather_info_inverness_fl"
		self.time_doc_id = "current_eastern_time"
		self.weather_metadata = {"source": "weather api"}
		self.time_metadata = {"source": "eastern time clock"}

		# Start the background tasks
		self.update_weather.start()
		self.update_time.start()

	async def cog_unload(self):
		self.update_weather.cancel()
		self.update_time.cancel()

	@tasks.loop(minutes=5)
	async def update_weather(self):
		api_key = omega.cfg.WEATHERAPICOM_API_KEY
		location = "Inverness,FL"
		url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(url) as resp:
					if resp.status != 200:
						print(f"Weather API error: {resp.status}")
						return
					data = await resp.json()
			text = (
				f"Weather in {location}:\n"
				f"{data['current']['condition']['text']}, "
				f"{data['current']['temp_f']}°F"
				f"(feels like {data['feelslike_f']}°F)."
			)

			await self._upsert_document(self.weather_doc_id, text, self.weather_metadata)

		except Exception as e:
			omega.logger.info(f"Weather update error: {e}.")

	@tasks.loop(seconds=15)
	async def update_time(self):
		try:
			tz = pytz.timezone("America/New_York")
			now = datetime.now(tz)
			text = f"The current time in Eastern Time (ET) is {now.strftime('%H:%M')}.\nThe current Date in Easter Time (ET) is {now.strftime('%Y-%m-%d')}"
			await self._upsert_document(self.time_doc_id, text, self.time_metadata)
		except Exception as e:
			omega.logger.info(f"Time update error: {e}.")

	async def _upsert_document(self, doc_id: str, new_text: str, metadata: dict):
		existing = omega.rag.collection.get(include=["metadatas", "documents"])
		ids = [md.get("id") for md in existing.get("metadatas", []) if md]
		if doc_id in ids:
			omega.rag.update_info_in_local_rag(doc_id, new_text)
		else:
			metadata_with_id = dict(metadata)
			metadata_with_id["id"] = doc_id
			omega.rag.add_info_to_local_rag(new_text, doc_id, metadata_with_id)

async def setup(bot: commands.Bot):
	cog = RagUpdater(bot)
	await bot.add_cog(cog)
