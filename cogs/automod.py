# cogs/automod.py

import re
from difflib import SequenceMatcher
from discord.ext import commands
from core.omega import omega

class AutoMod(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.profanity_list = self.load_profanity_list()

	def load_profanity_list(self):
		with open('./data/profanity.txt', 'r', encoding='utf-8') as f:
			return list(set(line.strip().lower() for line in f if line.strip()))

	def normalize(self, text: str):
		substitutions = {
			'1': 'i', '!': 'i', '3': 'e', '4': 'a', '@': 'a',
			'5': 's', '$': 's', '7': 't', '0': 'o'
		}
		for k, v in substitutions.items():
			text = text.replace(k, v)
		text = re.sub(r'[^a-zA-Z]', '', text)
		return text.lower()

	def is_similar(self, a: str, b: str):
		return SequenceMatcher(None, a, b).ratio() > 0.85

    # get the matched string so I can debug what string it matched
	def get_matched_string(self, a: str, b: str):
		return [x for x in self.profanity_list if self.is_similar(a, x)][0]
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		
		if not message.guild.me.guild_permissions.manage_messages:
			return

		normalized = self.normalize(message.content)
		for profanity in self.profanity_list:
			if profanity in normalized or self.is_similar(normalized, profanity):
				await message.delete()
				await message.channel.send(
					f"{message.author.mention}, your message contained inappropriate language and has been deleted.\n*This message will delete in 5 seconds.*",
					delete_after=5
				)
				matched_string = self.get_matched_string(normalized, profanity)
				with open('./data/automod_log.txt', 'a', encoding='utf-8') as f:
					f.write(f"{message.author.id}|{message.content}|{matched_string}\n")
				break

	@commands.command(name='automodstats')
	async def amrank(self, ctx):
		with open('./data/automod_log.txt', 'r', encoding='utf-8') as f:
			log_data = f.readlines()
			user_warnings = {}
			for line in log_data:
				user_id, _ = line.strip().split('|', 1)
				user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
			sorted_users = sorted(user_warnings.items(), key=lambda x: x[1], reverse=True)
			rank_list = [f"<@{user_id}>: {count} warnings" for user_id, count in sorted_users]
			await ctx.send("\n".join(rank_list))

async def setup(bot: commands.Bot):
	await bot.add_cog(AutoMod(bot))
