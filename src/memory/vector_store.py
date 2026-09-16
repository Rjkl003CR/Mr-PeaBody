import os
import importlib


try:
    chromadb = importlib.import_module("chromadb")
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "ChromaDB is required for memory storage. Install it with: pip install chromadb"
    ) from exc

chroma_path = os.getenv("CHROMA_PATH", "data/chroma_db")

# Initialize persistent local ChromaDB client
chroma_client = chromadb.PersistentClient(path=chroma_path)
collection = chroma_client.get_or_create_collection(name="mr_peabody_memories")

def save_memory(doc_id: str, content: str, source: str):
    """Stores a document/note in ChromaDB."""
    collection.add(
        documents=[content],
        metadatas=[{"source": source}],
        ids=[doc_id]
    )

def search_memory(query: str, n_results: int = 3):
    """Searches for relevant context matching the query."""
    results = collection.query(query_texts=[query], n_results=n_results)
    if results and results.get('documents') and len(results['documents']) > 0:
        return results['documents'][0]
    return []