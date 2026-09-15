#  Personal Memory AI Bot ("Second Brain")

A personal AI assistant designed to index, store, and instantly retrieve your private notes, saved links, preferences, and web content using **Retrieval-Augmented Generation (RAG)** and **Hybrid Vector Search**.

Instead of digging through saved chat messages or browser bookmarks, simply input raw notes or links. The bot extracts, embeds, and indexes them so you can recall exact links, context, or facts with a single word or semantic search.


##  Features

- **Link & Web Content Scraping:** Automatically fetches metadata, titles, and main text when you paste URLs.
- **Instant Keyword & Context Search:** Find items by exact terms (e.g., brand names, domain names) or semantic queries (e.g., *"that pasta recipe I saved last month"*).
- **Personalized RAG Engine:** Answers queries exclusively using your stored knowledge base with minimal hallucination.
- **Fast Access Interfaces:** Multi-platform support—use it via a lightweight web UI or directly through a Telegram/Discord bot interface on your phone.


##  Repository Structure

.
├── data/                    # Local ChromaDB persistent storage
├── src/
│   ├── ingestion/
│   │   ├── scraper.py       # Extract content from links & raw notes
│   │   └── parser.py        # Text chunking and cleaning utilities
│   ├── memory/
│   │   ├── vector_store.py  # ChromaDB/Qdrant collection setup
│   │   └── search.py        # Hybrid vector + keyword search logic
│   ├── bot/
│   │   ├── interface.py     # Telegram / Discord / Web bot handler
│   │   └── system_prompt.py # Personalized LLM persona & memory prompts
│   └── main.py              # Application entrypoint
├── .env.example             # Template for API keys & configuration
├── requirements.txt         # Python dependencies
└── README.md
