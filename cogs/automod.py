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
		return SequenceMatcher(None, a, b).ratio() > 0.95

	def get_matched_string(self, a: str, b: str):
		return [x for x in self.profanity_list if self.is_similar(a, x)][0]
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		
		if not message.guild.me.guild_permissions.manage_messages:
			return
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if not message.guild.me.guild_permissions.manage_messages:
			return

		normalized = self.normalize(message.content)
		matched_strings = []

		for profanity in self.profanity_list:
			if profanity in normalized or self.is_similar(normalized, profanity):
				matched_strings.append(self.get_matched_string(normalized, profanity))

		if matched_strings:
			await message.delete()
			
			command_names = ['wordcheck', 'checkword', 'wc']
			if any(message.content.startswith(omega.cfg.COMMAND_PREFIX + cmd) for cmd in command_names):
				return

			await message.channel.send(
				f"{message.author.mention}, your message contained inappropriate language and has been deleted.\n*This message will delete in 5 seconds.*",
				delete_after=5
			)

			with open('./data/automod_log.txt', 'a', encoding='utf-8') as f:
				for matched_string in matched_strings:
					f.write(f"{message.author.id}|{message.content}|{matched_string}\n")

	@commands.command(name='automodstats', aliases=['ams'])
	async def amrank(self, ctx):
		# check if file exists
		try:
			with open('./data/automod_log.txt', 'r', encoding='utf-8') as f:
				log_data = f.readlines()
				user_warnings = {}
				for line in log_data:
					user_id, _ = line.strip().split('|', 1)
					user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
				sorted_users = sorted(user_warnings.items(), key=lambda x: x[1], reverse=True)
				rank_list = [f"<@{user_id}>: {count} warnings" for user_id, count in sorted_users]
				if not rank_list:
					await ctx.send("No warnings found.")
					return
				await ctx.send("\n".join(rank_list))
		except FileNotFoundError:
			await ctx.send("No automod log found.")

	@commands.command(name='automodreset')
	async def amreset(self, ctx):
		with open('./data/automod_log.txt', 'w', encoding='utf-8') as f:
			f.write("")
		await ctx.send("Automod log has been reset.")
	
	@commands.command(name='wordcheck', aliases=['checkword', 'wc'])
	async def wordcheck(self, ctx, *, word: str):
		await message.delete()
		obfuscated_word = re.sub(r'[aeiou]', '\*', word, flags=re.IGNORECASE)
		await ctx.send(f"Checking automod logs for {obfuscated_word}")
		with open('./data/automod_log.txt', 'r', encoding='utf-8') as f:
			log_data = f.readlines()
			user_warnings = {}
			for line in log_data:
				user_id, message, matched_string = line.strip().split('|', 2)
				if matched_string == word:
					user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
			sorted_users = sorted(user_warnings.items(), key=lambda x: x[1], reverse=True)[:10]
			rank_list = [f"<@{user_id}>: {count} times" for user_id, count in sorted_users]
			await ctx.send(f"{obfuscated_word}: {len(user_warnings)} times detected\n" + "\n".join(rank_list))
	
	@commands.command(name='banword')
	@commands.has_permissions(manage_messages=True)
	async def add_word(self, ctx, *, word: str):
		with open('./data/profanity.txt', 'a', encoding='utf-8') as f:
			f.write(f"{word.lower()}\n")
		self.profanity_list.append(word.lower())
		await ctx.send(f"Added {word} to the profanity list.")
	
	@commands.command(name='unbanword')
	@commands.has_permissions(manage_messages=True)
	async def remove_word(self, ctx, *, word: str):
		with open('./data/profanity.txt', 'r', encoding='utf-8') as f:
			lines = f.readlines()
		with open('./data/profanity.txt', 'w', encoding='utf-8') as f:
			for line in lines:
				if line.strip().lower() != word.lower():
					f.write(line)
		self.profanity_list.remove(word.lower())
		await ctx.send(f"Removed {word} from the profanity list.")
	

async def setup(bot: commands.Bot):
	await bot.add_cog(AutoMod(bot))
