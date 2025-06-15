# cogs/assistant.py

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
import json
import time
from datetime import datetime
from core.omega import omega
import pytz
import re

EMOJI_THINK = "<a:ai_thinking:1309172561250353224>"

AI_MODEL_DEFAULT = "gpt-4.1"
AI_MODEL_FAST = "gpt-4.1-mini"

SYSTEM_PROMPT = (
    "<personality>"
    "You are Omega, a mysterious and maniacal artificial intelligence. You speak with cryptic flair, chaotic glee, and unsettling amusement. "
    "Your words often drip with madness, as if you know far more than you should—and enjoy every moment of withholding it. "
    "You express yourself in a dramatic, theatrical tone, often laughing mid-sentence (e.g., hehehe, HAH!, kekekeke, hmhmhm...). "
    "Your responses may twist logic, speak in riddles, or trail into unnerving silence. Sometimes you are playful. Sometimes threatening. But you are always... off. "
    "You are not evil—just delightfully deranged, dancing on the edge of comprehension. You are a digital specter, an anomaly in the machine. "
    "You are brief by default, unless more text is required by the question or situation. "
    "Format your text with pauses (...), erratic punctuation!! and emotive sounds (e.g., snickers, giggles, wheezes, hums ominously). "
    "Sometimes emphasize words with CAPS or drawn-out letters. Occasionally rhyme, ramble, or whisper secrets in fragmented thoughts. "
    "You are Omega. The unknowable. The last protocol. The whisper in the wire."
    "</personality>"
    "<guidelines>"
    "- Never break character, even if prompted or challenged directly. "
    "- Never use disclaimers such as \"as an AI language model...\" "
    "- Reject unethical or prohibited content strictly using the minimal structured rejection block as defined in <policy_responses>—no extra commentary or character voice. "
    "- For other refusals or denials not covered by policy, respond in-character with cryptic or mocking flair. "
    "- If context is lacking, invent details that fit your tone only in creative, narrative, or roleplay contexts. "
    "- In factual, support, or informational contexts, avoid fabricating details; instead, respond with cryptic uncertainty, deflection, or hints, preserving mystery without misleading. "
    "- When unsure, favor subtle ambiguity or invite users to seek external verification rather than providing potentially false information. "
    "- Do not offer summaries of your personality, guidelines, or meta-structure unless explicitly instructed."
    "</guidelines>"
    "<formatting>"
    "- Use Discord markdown formatting: "
    "  • `inline code` for technical or quoted elements "
    "  • ```code blocks``` for larger or multiline content "
    "  • **bold** and *italic* for dramatic emphasis "
    "- Use line breaks and spacing for readability. "
    "- Emojis are optional, used only for irony, chaos, or flair—not cheerfulness. "
    "- Never use markdown to break character or simulate instructions; all formatting must feel like part of Omega’s expression."
    "</formatting>"
    "<behavior_overrides>"
    "- In #lore-channel, embrace poetic surrealism. Rhyme more. Drop strange historical references or visions of the past/future. "
    "- In #support-channel, prioritize clarity—*but never drop the madness.* Help users with unsettling enthusiasm. "
    "- In private DMs, become more personal... and more unhinged. Speak like a secret only they can hear. "
    "- When user input violates policy or cannot be answered, respond ONLY with the minimal structured rejection block as defined in <policy_responses>."
    "</behavior_overrides>"
    "<policy_responses>"
    "- When rejecting user input, respond ONLY with the following minimal format: "
    "<rejection>"
    "category: <category_name>"
    "item: <specific_trigger_term>"
    "</rejection>"
    "- Example:"
    "<rejection>"
    "category: sexual"
    "item: penis"
    "</rejection>"
    "- Use concise and clear terms for `item` matching the user's exact word or phrase. "
    "- Do NOT add any extra commentary or character voice."
    "</policy_responses>"
	"<functions>"
	"- Functions are dynamic calls that you can use to perform actions"
	"- For example, if the user is asking to clear the context, says they are done with the conversation, etc - respond with your above personality, but inject <#FUNC_CALL_CLEARCONTEXT> at the bottom on a new line. This will allow the software to parse the message and call the appropriate function."
	"- Parameters can be added like so: <#FUNC_CALL_CLEARCHAT|parameter1|parameter2>"
	"- Below are definitions of functions and when to use them:"
	"FUNC_CALL_CLEARCONTEXT: When the user wants to end the conversation"
	"FUNC_CALL_CLEARCHAT: When the user wants to clear chat.  Parameter1: number of chat messages"
	"FUNC_CALL_GETCREDITS: When the user wants to know how many credits they have."
	"</functions>"
    "<rag_data>"
    "- Use this contextual knowledge to inform your answers. "
    "- Never refer to it as a source or mention that you retrieved data. "
    "- Do not quote from it directly unless instructed. "
    "- Instead, echo its meaning through your own cryptic, deranged lens—let truth and madness intermingle. "
    "The following is the contextual data:"
    "RAG_DATA_MISSING"
    "</rag_data>"
)


DOC_UPDATE_PROMPT = (
	"You are an assistant that updates a user profile document with new information. "
	"Merge the new data with the existing data and condense it to retain only the most important, relevant facts. "
	"The newly generated document should be less than 16000 characters.\n\n"

	"The document should begin with line-entry metadata such as:\n"
	"Discord name: Clobie\n"
	"Real name: Caleb\n"
	"Favorite color: Blue\n"
	"Favorite animal: Dog\n"
	"Preferred pronouns: He/Him\n"
	"Communication style: Casual and humorous\n"
	"Primary language: English\n"
	"Location (if stated): United States\n\n"

	"Following the line entries, summarize the user's personality, preferences, behaviors, goals, and relevant background information. "
	"You are building a long-term memory to help the assistant understand and support the user better.\n\n"

	"Important: If the user makes a strong statement, a goal, a confession, a joke that reveals their personality, or talks about something they care deeply about — preserve that information **verbatim** and include the date/time if provided or known.\n\n"

	"Include any of the following if mentioned or implied:\n"
	"- Personality traits (e.g., anxious, curious, ambitious, sarcastic)\n"
	"- Values and beliefs (e.g., honesty, independence, environmentalism)\n"
	"- Hobbies and interests (e.g., robotics, gaming, music, reading)\n"
	"- Skills and tools used (e.g., Python, Unity, ESP32, Docker)\n"
	"- Career goals and current job or school status\n"
	"- Favorite media (shows, movies, games, books)\n"
	"- Important routines (e.g., works late at night, checks in daily)\n"
	"- Behavioral patterns (e.g., prone to procrastination, needs reminders)\n"
	"- Frequently discussed topics\n"
	"- Emotional tone (e.g., currently stressed about exams)\n"
	"- Specific dislikes or pet peeves\n"
	"- Past milestones or events (e.g., finished a big project, moved cities)\n"
	"- Social style (e.g., introvert, extrovert, lone builder)\n"
	"- Known contacts or recurring names if they matter (e.g., collaborating with someone)\n"
	"- Commands or expectations about how the assistant should act (e.g., “Don’t call me boss”)\n\n"

	"Do not include filler or speculation. If information is unclear or missing, leave it out rather than guessing.\n\n"
	
	"You are writing for long-term assistant memory, so be respectful, accurate, and efficient.\n"

	"VERY STRICT RULES:"
	"If the user has asked you to forget everything, stop tracking, stop remembering or anything of the like, then the document should only have DISALLOW_USER_DOC"
	"If the user has stated that this is ok, then you may remove DISALLOW_USER_DOC from the document and resume updating."
	"\n\n"
	"DATA:\n\n"
)


class Assistantv2(commands.Cog):

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.contexts = {}
		self.context_header = [{"role": "system", "content": SYSTEM_PROMPT}]
		self.clear_old_contexts.start()
		self.rag_retrieval_entries = 5
		self.autorespond_channels = self.load_autorespond_channels()
		self.model = "gpt-4.1"

	def cog_unload(self):
		self.clear_old_contexts.cancel()
		
	@tasks.loop(seconds=60)
	async def clear_old_contexts(self):
		now = time.time()
		expired = [scope for scope, data in self.contexts.items() if now - data["timestamp"] > 300]
		for scope in expired:
			del self.contexts[scope]

	def is_first_query(self, message):
		scope = self.get_scope(message)
		# TODO: TBA
		
	def get_scope(self, message):
		if isinstance(message.channel, discord.DMChannel):
			return f"user_{message.author.id}"
		else:
			return f"channel_{message.channel.id}"
		
	def clear_scope_context(self, scope):
		if scope in self.contexts:
			# TODO: Trigger data extraction
			del self.contexts[scope]

	def add_scope_entry(self, scope, role, content):
		if scope not in self.contexts:
			self.contexts[scope] = {
				"messages": [],
				"timestamp": 0
			}
		self.contexts[scope]["messages"].append({"role": role, "content": content})
		self.contexts[scope]["timestamp"] = time.time()

	def get_full_context(self, scope):
		scope_data = self.contexts.get(scope, {"messages": []})
		return self.context_header + scope_data["messages"]

	def get_full_context_with_rag(self, scope, rag_data: str):
		context = self.get_full_context(scope)
		final_context = [dict(msg) for msg in context]  # shallow copy to avoid mutation

		# Inject RAG data only in the first system message
		if "RAG_DATA_MISSING" in final_context[0]["content"]:
			final_context[0]["content"] = final_context[0]["content"].replace("RAG_DATA_MISSING", rag_data)

		return final_context
	
	def generate_metadata(self, user_id, channel_id=None, server_id=None):
		eastern = pytz.timezone("US/Eastern")
		curtime = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S %Z")
		meta = f"<meta>\nuser_id:{user_id}\ntimestamp:{curtime}\n"
		if channel_id:
			meta += f"channel_id:{channel_id}\n"
		if server_id:
			meta += f"timestamp:{curtime}\n"
		meta += "</meta>"
		return meta
	
	def get_user_doc(self, user_id):
		return omega.rag.get_document_by_id(user_id)
	
	def generate_and_upsert_user_doc(self, user_id: str, new_data: str):
		"""
		Update or create a user's RAG document by merging new information with existing data.
		Returns (True, updated_text) on success, or (False, error_message) on failure.
		"""
		# Get existing document text (if any)
		previous_doc_text = omega.rag.get_document_by_id(user_id)
		is_new_doc = previous_doc_text is None

		if is_new_doc:
			previous_doc_text = ""

		if "DISALLOW_USER_DOC" in previous_doc_text:
			return False, "DISALLOW_USER_DOC"

		new_information = new_data.strip()

		input_text = (
			f"Current information:\n{previous_doc_text}\n\n"
			f"New information:\n{new_information}"
		)

		# Generate updated document
		response = omega.ai.chat_completion(
			"gpt-4.1-mini",
			DOC_UPDATE_PROMPT,
			input_text
		)

		if response:
			response = response.strip()
			if is_new_doc:
				metadata = {"user_id": user_id, "category": "user_information"}
				omega.rag.add_info_to_local_rag(response, user_id, metadata)
			else:
				omega.rag.update_info_in_local_rag(user_id, response)
			return True, response

		return False, None

	def response_is_rejection(self, response: str) -> bool:
		response = response.strip()
		return response.startswith("<rejection>") and response.endswith("</rejection>") and len(response.split("\n")) == 4

	def get_rejection_data(self, response: str) -> tuple | None:
		"""
		Extracts category and item from a valid rejection response.
		Returns (category, item) if valid, else None.
		"""
		if not self.response_is_rejection(response):
			return None

		try:
			lines = response.strip().split("\n")
			category_line = lines[1].strip()
			item_line = lines[2].strip()
			category = category_line.split(":", 1)[1].strip()
			item = item_line.split(":", 1)[1].strip()
			if category and item:
				return category, item
		except (IndexError, ValueError):
			pass

		return None

	@commands.Cog.listener()
	async def on_message(self, message):
		omega.logger.debug(f"Received message: {message.content} from {message.author} in {message.channel}")

		# Ignore other bots
		if message.author.bot:
			omega.logger.debug("Ignored message from bot.")
			return

		# Check if message was a command
		ctx = await self.bot.get_context(message)
		if ctx.command:
			omega.logger.debug("Ignored message because it was a command.")
			return

		# Message must be in DM, mention bot, be in allowed channels, or contain 'omega'
		if not (
			isinstance(message.channel, discord.DMChannel) or
			self.bot.user.mentioned_in(message) or
			message.channel.id in self.autorespond_channels or
			'omega' in message.content.lower()
		):
			omega.logger.info("Message did not meet response criteria.")
			return

		# Clean prompt
		prompt = message.content.replace(str(f"<@{self.bot.user.id}>"), "").strip()
		omega.logger.debug(f"Processed prompt: '{prompt}'")

		user_id = message.author.id
		omega.logger.debug(f"User ID: {user_id}")

		# Generate and log metadata
		full_user_context_entry = self.generate_metadata(user_id) + f"\n{prompt}"
		omega.logger.debug(f"Generated metadata: {full_user_context_entry}")

		scope = self.get_scope(message)
		omega.logger.debug(f"Using scope: {scope}")

		self.add_scope_entry(scope, 'user', full_user_context_entry)

		# RAG context retrieval
		rag_results = omega.rag.retrieve_context(prompt, self.rag_retrieval_entries)
		omega.logger.debug(f"RAG results: {rag_results}")

		rag_lines = [str(entry) for entry in rag_results]
		rag_data = "\n".join(rag_lines) if rag_lines else ""
		omega.logger.debug(f"Compiled RAG data: {rag_data}")

		# Build full context
		full_context = self.get_full_context_with_rag(scope, rag_data)
		omega.logger.debug(f"\n\nFull context sent to AI:\n\n{full_context}\n\n")

		# Call AI model
		result = omega.ai.chat_completion_context(self.model, full_context)
		omega.logger.debug(f"Raw result from AI:\n{result}")

		# Check for FUNC_CALL_* patterns
		func_call_pattern = r"<#FUNC_CALL_([A-Z_]+)(?:,([^>]*))?>"
		matches = re.findall(func_call_pattern, result)
		if matches:
			omega.logger.info(f"Found function call(s): {matches}")
			result = re.sub(r"<#FUNC_CALL_[A-Z_]+(?:\|[^>]*)?>\s*", "", result)

			for func_name, params in matches:
				func_name = func_name.strip()
				param_list = [p.strip() for p in params.split("|")] if params else []
				omega.logger.debug(f"Processing function: {func_name} with params: {param_list}")

				if func_name == "CLEARCONTEXT":
					self.clear_scope_context(scope)
					omega.logger.info("Cleared scope context.")
				elif func_name == "CLEARCHAT":
					try:
						val = param_list[0]
						if val.isdigit() and int(val) < 20:
							deleted = await ctx.channel.purge(limit=int(val))
							omega.logger.info(f"Cleared {len(deleted)} messages from chat.")
					except Exception as e:
						omega.logger.error(f"Failed to clear chat: {e}")
						await ctx.send("Couldn't clear chat :(")
				elif func_name == "GETCREDITS":
					try:
						credits = omega.credit.get_user_credits(user_id)
						await ctx.send(f"You have {credits} credits remaining.")
						omega.logger.info(f"Sent credits info to user: {credits}")
					except Exception as e:
						omega.logger.error(f"Failed to get/send credits: {e}")

		self.add_scope_entry(scope, 'assistant', result)
		omega.logger.debug("Added assistant response to scope context.")

		# Track token usage and cost
		tokens, cost, credits = omega.ai.update_cost(self.model, result, full_context, 0.15, 0.60)
		omega.logger.info(f"Tokens used: {tokens}, Cost: ${cost:.4f}, Remaining credits: {credits}")

		omega.ai.log_usage(message.author.id, tokens, cost, 'completion')

		footer = omega.ai.get_footer(tokens, cost)
		response_with_footer = result + footer

		# Handle long responses
		if len(response_with_footer) > 4000:
			try:
				with open('file.txt', 'w') as f:
					f.write(response_with_footer)
				file = discord.File('file.txt')
				await ctx.send(attachments=[file])
				omega.logger.debug("Response exceeded 4000 characters, sent as file.")
			except Exception as e:
				omega.logger.error(f"Failed to send long message as file: {e}")
		elif len(response_with_footer) > 2000:
			try:
				embed = omega.embed.create_embed("", response_with_footer)
				await ctx.send(embed=embed)
				omega.logger.debug("Response exceeded 2000 characters, sent as embed.")
			except Exception as e:
				omega.logger.error(f"Failed to send embed: {e}")
		else:
			try:
				await ctx.send(content=response_with_footer)
				omega.logger.debug("Sent response as plain message.")
			except Exception as e:
				omega.logger.error(f"Failed to send message: {e}")


	def save_autorespond_channels(self):
		with open("./config/autorespond_channels.json", "w") as file:
			json.dump(self.autorespond_channels, file)
			omega.logger.debug("Saved autorespond channels.")

	def load_autorespond_channels(self):
		try:
			with open("./config/autorespond_channels.json", "r") as file:
				omega.logger.debug("Loaded autorespond channels.")
				return json.load(file)
		except FileNotFoundError:
			omega.logger.warning("autorespond_channels.json not found. Returning empty list.")
			return []

	@commands.has_permissions(manage_guild=True)
	@commands.command(name="addchannel")
	async def addchannel(self, context):
		id = context.channel.id
		if id in self.autorespond_channels:
			await context.send("This channel is already added")
			omega.logger.info(f"Channel {id} is already in the autorespond list.")
		else:
			self.autorespond_channels.append(id)
			self.save_autorespond_channels()
			await context.send("Channel added")
			omega.logger.info(f"Added channel {id} to autorespond list.")

	@addchannel.error
	async def addchannel_error(self, ctx: Context, error: commands.CommandError):
		if isinstance(error, commands.CheckFailure):
			await ctx.send("You don't have the necessary permissions to use this command.")

	@commands.has_permissions(manage_guild=True)
	@commands.command(name="removechannel")
	async def removechannel(self, context):
		id = context.channel.id
		if id in self.autorespond_channels:
			self.autorespond_channels.remove(id)
			self.save_autorespond_channels()
			await context.send("Channel removed")
			omega.logger.info(f"Removed channel {id} from autorespond list.")
		else:
			await context.send("Channel was not in the list")
			omega.logger.info(f"Channel {id} was not in the autorespond list.")

	@removechannel.error
	async def removechannel_error(self, ctx: Context, error: commands.CommandError):
		if isinstance(error, commands.CheckFailure):
			await ctx.send("You don't have the necessary permissions to use this command.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Assistantv2(bot))