# cogs/rag_test.py

import discord
import asyncio
from discord.ext import commands
from core.omega import omega

class RagTest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.has_permissions(administrator=True)
    @commands.command(name="testadd")
    async def testadd(self, ctx,  *, data: str):
        omega.rag.add_info_to_local_rag(data, metadata={"source": "testadd command"})
        await ctx.send("Added test entry to local RAG.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="testretrieve")
    async def testretrieve(self, ctx, *, query: str):
        results = omega.rag.retrieve_context(query, top_k=4)
        if not results:
            await ctx.send("No documents found.")
            return

        # Convert all entries to strings (even if they are already strings, this is safe)
        texts = [str(entry) for entry in results]

        msg = "\n\n".join(texts)
        if len(msg) > 1900:
            msg = msg[:1900] + "\n...[truncated]"
        await ctx.send(f"Top results for '{query}':\n{msg}")
    
    @commands.has_permissions(administrator=True)
    @commands.command(name="testdelete")
    async def testdelete(self, ctx, *, query: str):
        # Encode query embedding
        embedding = omega.rag.embedder.encode([query])[0]

        # Query collection WITHOUT 'ids' in include
        query_results = omega.rag.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=10,
            include=["documents", "metadatas"]  # no "ids"
        )

        docs = query_results['documents'][0]
        metadatas = query_results['metadatas'][0]

        if not docs:
            await ctx.send("No documents found for that query.")
            return

        # Extract ids from metadata
        ids = [md.get("id", None) for md in metadatas]

        # Prepare message for user selection
        msg_lines = ["Select the number of the document to delete:"]
        for i, doc in enumerate(docs, start=1):
            preview = doc[:100].replace("\n", " ")
            msg_lines.append(f"{i}. {preview}")
        msg_lines.append(f"{len(docs)+1}. Delete ALL results")
        msg_lines.append("Reply with the number corresponding to your choice.")

        await ctx.send("\n".join(msg_lines))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            reply = await self.bot.wait_for("message", timeout=30.0, check=check)
            choice = int(reply.content.strip())
        except (asyncio.TimeoutError, ValueError):
            await ctx.send("Invalid input or timeout. Cancelled delete operation.")
            return

        if choice < 1 or choice > len(docs) + 1:
            await ctx.send("Choice out of range. Cancelled delete operation.")
            return

        if choice == len(docs) + 1:
            # Delete all found documents (filter out None IDs)
            valid_ids = [id_ for id_ in ids if id_]
            if valid_ids:
                omega.rag.collection.delete(ids=valid_ids)
                await ctx.send(f"Deleted all {len(valid_ids)} matching documents.")
            else:
                await ctx.send("No valid document IDs found to delete.")
        else:
            del_id = ids[choice - 1]
            if del_id:
                omega.rag.collection.delete(ids=[del_id])
                await ctx.send(f"Deleted document #{choice}.")
            else:
                await ctx.send("Selected document does not have a valid ID; cannot delete.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="listentries")
    async def listentries(self, ctx):
        all_data = omega.rag.collection.get(include=["documents", "metadatas"])
        documents = all_data.get("documents", [])
        metadatas = all_data.get("metadatas", [])

        if not documents:
            await ctx.send("The database is empty.")
            return

        ids = [md.get("id", "N/A") if md else "N/A" for md in metadatas]

        lines = ["Entries in the RAG database:"]
        for i, (doc, doc_id) in enumerate(zip(documents, ids), start=1):
            preview = doc[:100].replace("\n", " ")
            lines.append(f"{i}. ID: `{doc_id}` - {preview}")

        message = "\n".join(lines)
        if len(message) > 1900:
            chunks = []
            current_chunk = []
            current_len = 0
            for line in lines:
                if current_len + len(line) + 1 > 1900:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                current_chunk.append(line)
                current_len += len(line) + 1
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(message)

@commands.has_permissions(administrator=True)
@commands.command(name="testupdate")
async def testupdate(self, ctx, doc_id: str):
	await ctx.send(f"Looking up document with ID `{doc_id}`...")

	# Try to retrieve the document and metadata
	results = omega.rag.collection.get(
		ids=[doc_id],
		include=["documents", "metadatas"]
	)

	docs = results.get("documents", [])
	metas = results.get("metadatas", [])

	if not docs:
		await ctx.send(f"❌ No document found with ID `{doc_id}`.")
		return

	# Show current data to user
	current_text = docs[0]
	current_meta = metas[0] if metas else {}

	# Format metadata as JSON string for readability
	import json
	meta_display = json.dumps(current_meta, indent=2)

	# Truncate if too long for Discord
	if len(current_text) > 1000:
		current_text_display = current_text[:1000] + "\n...[truncated]"
	else:
		current_text_display = current_text

	await ctx.send(
		f"**Current document:**\n```{current_text_display}```\n\n"
		f"**Current metadata:**\n```json\n{meta_display}```"
	)

	# Prompt for new content
	await ctx.send(f"Please provide the *new content* for document ID `{doc_id}`:")

	def check(m):
		return m.author == ctx.author and m.channel == ctx.channel

	try:
		reply = await self.bot.wait_for("message", timeout=120.0, check=check)
		new_text = reply.content.strip()
	except asyncio.TimeoutError:
		await ctx.send("⏰ Timeout: No content received. Update cancelled.")
		return

	# Ask if user wants to change metadata
	await ctx.send("Would you like to add or update metadata as well? Reply with `yes` or `no`:")

	try:
		meta_reply = await self.bot.wait_for("message", timeout=30.0, check=check)
		wants_metadata = meta_reply.content.lower() in ["yes", "y"]
	except asyncio.TimeoutError:
		await ctx.send("Timeout. Proceeding without metadata.")
		wants_metadata = False

	new_metadata = None
	if wants_metadata:
		await ctx.send("Please provide metadata as JSON (e.g. `{\"source\": \"user update\"}`):")
		try:
			json_reply = await self.bot.wait_for("message", timeout=60.0, check=check)
			new_metadata = json.loads(json_reply.content)
		except (asyncio.TimeoutError, json.JSONDecodeError):
			await ctx.send("⚠️ Invalid or no JSON received. Proceeding without metadata.")

	# Perform the update
	omega.rag.update_info_in_local_rag(doc_id, new_text, new_metadata)
	await ctx.send(f"✅ Document with ID `{doc_id}` has been updated.")





async def setup(bot: commands.Bot):
    cog = RagTest(bot)
    await bot.add_cog(cog)
