# utils/chroma.py

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from collections import defaultdict

class ChromaRAG:
    def __init__(self):
        """Initialize Chroma with an embedder and persistent local database."""
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma = chromadb.PersistentClient(path="./rag_db")
        self.collection = self.chroma.get_or_create_collection("discord_knowledge")
		
    def add_info_to_local_rag(self, text: str, metadata: dict = None):
        """Add a piece of text, its embedding, and optional metadata to the local RAG database."""
        embedding = self.embedder.encode([text])[0]
        add_kwargs = {
            "documents": [text],
            "embeddings": [embedding.tolist()],
            "ids": [str(hash(text))]
        }
        if metadata:
            add_kwargs["metadatas"] = [metadata]
        self.collection.add(**add_kwargs)

    def update_info_in_local_rag(self, doc_id: str, new_text: str, new_metadata: dict = None):
        """
        Update the document, embedding, and optional metadata for an existing entry by its ID.
        If the ID doesn't exist, this will add a new entry with that ID.
        """
        embedding = self.embedder.encode([new_text])[0]
        # Delete the old entry first (if exists)
        self.collection.delete(ids=[doc_id])
        
        add_kwargs = {
            "documents": [new_text],
            "embeddings": [embedding.tolist()],
            "ids": [doc_id]
        }
        if new_metadata:
            add_kwargs["metadatas"] = [new_metadata]
        self.collection.add(**add_kwargs)

    def retrieve_context(self, query: str, top_k=4) -> list[str]:
        """Retrieve top_k most relevant documents for a query."""
        embedding = self.embedder.encode([query])[0]
        results = self.collection.query(query_embeddings=[embedding.tolist()], n_results=top_k)
        return results['documents'][0] if results['documents'] else []
    
    def remove_info_from_local_rag(self, text: str):
        """Remove a document from the database using its text content."""
        doc_id = str(hash(text))
        self.collection.delete(ids=[doc_id])

    def remove_duplicates(self):
        """Remove duplicate documents from the collection, keeping the first occurrence."""
        all_docs = self.collection.get(include=["documents", "ids"])
        seen_texts = set()
        ids_to_delete = []
        for doc, doc_id in zip(all_docs["documents"], all_docs["ids"]):
            if doc in seen_texts:
                ids_to_delete.append(doc_id)
            else:
                seen_texts.add(doc)
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)