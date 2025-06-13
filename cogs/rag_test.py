# cogs/rag_test.py

import discord
import asyncio
from discord.ext import commands
from core.omega import omega

class RagTest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.has_permissions(administrator=True)
    @commands.command(name="ragadd")
    async def ragadd(self, ctx,  *, data: str):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        omega.rag.add_info_to_local_rag(data)
        await ctx.send("Added test entry to local RAG.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="ragsearch")
    async def ragsearch(self, ctx, *, query: str):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        results = omega.rag.retrieve_context(query, top_k=4)
        if not results:
            await ctx.send("No documents found.")
            return
        texts = [str(entry) for entry in results]
        msg = "\n\n".join(texts)
        if len(msg) > 1900:
            msg = msg[:1900] + "\n...[truncated]"
        await ctx.send(f"Top results for '{query}':\n{msg}")
    
    @commands.has_permissions(administrator=True)
    @commands.command(name="ragdeletesearch")
    async def ragdeletesearch(self, ctx, *, query: str):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        embedding = omega.rag.embedder.encode([query])[0]
        query_results = omega.rag.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=10,
            include=["documents", "metadatas"]
        )
        docs = query_results['documents'][0]
        metadatas = query_results['metadatas'][0]
        if not docs:
            await ctx.send("No documents found for that query.")
            return
        ids = [md.get("id", None) for md in metadatas]
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
    @commands.command(name="ragsearch")
    async def ragsearch(self, ctx):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
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
    @commands.command(name="ragupdatedoc")
    async def ragupdatedoc(self, ctx, doc_id: str):
        if not ctx.author.id == int(omega.cfg.BOT_OWNER):
            await ctx.send("You do not have the required permissions for that command.")
            return
        await ctx.send(f"Looking up document with ID `{doc_id}`...")
        results = omega.rag.collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"]
        )
        docs = results.get("documents", [])
        metas = results.get("metadatas", [])
        if not docs:
            await ctx.send(f"❌ No document found with ID `{doc_id}`.")
            return
        current_text = docs[0]
        current_meta = metas[0] if metas else {}
        import json
        meta_display = json.dumps(current_meta, indent=2)
        if len(current_text) > 1000:
            current_text_display = current_text[:1000] + "\n...[truncated]"
        else:
            current_text_display = current_text
        await ctx.send(
            f"**Current document:**\n```{current_text_display}```\n\n"
            f"**Current metadata:**\n```json\n{meta_display}```"
        )
        await ctx.send(f"Please provide the *new content* for document ID `{doc_id}`:")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            reply = await self.bot.wait_for("message", timeout=120.0, check=check)
            new_text = reply.content.strip()
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timeout: No content received. Update cancelled.")
            return
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
        omega.rag.update_info_in_local_rag(doc_id, new_text, new_metadata)
        await ctx.send(f"✅ Document with ID `{doc_id}` has been updated.")





async def setup(bot: commands.Bot):
    cog = RagTest(bot)
    await bot.add_cog(cog)
