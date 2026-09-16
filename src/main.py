import os
import sys
import uuid
import re
from google import genai
from google.genai import types

from src.ingestion.scraper import scrape_url
from src.memory.vector_store import save_memory, search_memory

def load_dotenv() -> None:
    """Load simple KEY=VALUE entries from the project's .env file."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.isfile(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(
                key.strip(), value.strip().strip('"').strip("'")
            )


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file!")

# Initialize Google GenAI Client
client = genai.Client(api_key=api_key)

def process_and_save(input_text: str):
    """Processes URLs using scrape_url or stores text notes directly."""
    url_match = re.search(r"https?://\S+", input_text)
    
    if url_match:
        target_url = url_match.group(0)
        try:
            scraped_data = scrape_url(target_url)
            content = f"Title: {scraped_data.title}\nURL: {scraped_data.url}\nDescription: {scraped_data.description}\nContent: {scraped_data.text}"
            source = target_url
        except Exception as e:
            content = f"URL: {target_url} (Failed to scrape: {str(e)})"
            source = target_url
    else:
        content = input_text
        source = "user_note"
        
    doc_id = str(uuid.uuid4())
    save_memory(doc_id=doc_id, content=content, source=source)
    return source


def ask_mr_peabody(query: str) -> str:
    """Retrieves memories and generates answers in Mr. Peabody's persona."""
    retrieved_docs = search_memory(query)
    context_str = "\n---\n".join(retrieved_docs) if retrieved_docs else "No matching stored memories found."
    
    # Put system instructions directly inside the prompt text
    prompt = f"""You are Mr. Peabody, an extraordinarily intelligent, polite, and articulate personal AI memory assistant.
Answer the user accurately using ONLY the retrieved memories provided below. If a link or note is found, present it clearly with its direct context.

RETRIEVED MEMORIES:
{context_str}

USER QUESTION: {query}"""

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    return response.text