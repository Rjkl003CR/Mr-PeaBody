# SRS - Mr. PeaBody

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document details the functional and non-functional requirements for Mr. Peabody, an AI-powered personal memory assistant ("Second Brain"). The system captures, indexes, processes, and retrieves unstructured personal text notes, saved web links, and user preferences using Retrieval-Augmented Generation (RAG) and hybrid vector search.

### 1.2 Document Conventions

- **Must / Shall:** Mandates a required system feature or capability.
- **Should:** Indicates a recommended feature.
- **May:** Indicates an optional feature.

### 1.3 Intended Audience

This document is intended for software developers, system architects, and testers responsible for implementing, maintaining, and deploying the Mr. Peabody project.

## 2. Overall Description

### 2.1 Product Perspective

Mr. Peabody operates as a standalone personal assistant system composed of an Ingestion Engine, a Vector Database, an LLM Orchestration Layer, and lightweight User Interfaces (Telegram Bot and/or Web Dashboard). It acts as a single point of entry for saving and querying user context.

```text
+---------------------------------------------------------------------------------+
|                                 USER INTERFACE                                  |
|                 (Telegram Bot / Web App / REST API Endpoint)                    |
+----------------------------------------+----------------------------------------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
                       v                                   v
             [ Ingestion Engine ]                [ Search & RAG Engine ]
                       |                                   |
                       v                                   v
         +---------------------------+           +-------------------+
         | Web Scraper & Text Parser |           | ChromaDB /        |
         +-------------+-------------+           | Hybrid Vector DB  |
                       |                         +---------+---------+
                       +-----------------------------------+
```

### 2.2 Product Functions

- Parse incoming text messages and extract full page content from posted URLs.
- Convert text chunks into high-dimensional vector embeddings.
- Perform hybrid retrieval (combining exact keyword search and semantic vector similarity).
- Generate contextual answers adopting the "Mr. Peabody" persona.

## 3. System Features & Functional Requirements

### 3.1 Data Ingestion Module

#### 3.1.1 URL Scraping & Note Processing

- **FR-1.1:** The system shall detect URLs inside incoming user inputs.
- **FR-1.2:** If a URL is detected, the system shall scrape web page titles, metadata, and core body text, truncating content safely to prevent token overflow.
- **FR-1.3:** If plain text or notes are provided, the system shall extract text directly and auto-generate timestamp metadata.

#### 3.1.2 Data Chunking & Storage

- **FR-1.4:** Raw incoming text and scraped content shall be split into manageable text chunks (for example, 300-500 tokens).
- **FR-1.5:** Chunks shall be embedded using an embedding model (for example, OpenAI `text-embedding-3-small` or a local embedding model) and persisted to ChromaDB.

### 3.2 Retrieval & RAG Query Engine

#### 3.2.1 Hybrid Search

- **FR-2.1:** The system shall execute hybrid search (combining exact keyword matching and semantic similarity) against stored vector collections.
- **FR-2.2:** The retrieval layer shall return top-matching documents along with source metadata (for example, original URLs and creation dates).

#### 3.2.2 Persona-Based Generation

- **FR-2.3:** The system shall inject retrieved memories into the LLM system prompt formatted under the Mr. Peabody persona.
- **FR-2.4:** The LLM shall ground its answers strictly in the retrieved user data to prevent false hallucinations.
- **FR-2.5:** If no relevant data is found in the database, the system shall state that the topic has not yet been saved to Mr. Peabody's records.

### 3.3 User Interfaces

#### 3.3.1 Bot / Web Listener

- **FR-3.1:** The system shall expose webhooks or API endpoints compatible with messaging interfaces (for example, the Telegram Bot API).
- **FR-3.2:** The interface shall support separate execution paths for saving memories and querying the memory database.

## 4. Non-Functional Requirements

| Requirement ID | Category | Requirement Description |
| --- | --- | --- |
| NFR-1 | Performance | Vector search and LLM context generation shall return responses within 3 seconds for standard text queries. |
| NFR-2 | Security | API keys (OpenAI and Telegram tokens) must be managed exclusively via `.env` files and never committed to source control. |
| NFR-3 | Portability | The project shall run on cross-platform Python 3.10+ environments (Windows, macOS, and Linux). |
| NFR-4 | Data Integrity | ChromaDB data storage shall persist locally under `./data/chroma_db` across system restarts. |
| NFR-5 | Scalability | The database design shall support at least 10,000 unique document chunks without performance degradation. |

## 5. Dependencies

- Python >= 3.10
- ChromaDB
- OpenAI
- beautifulsoup4
- requests
- python-telegram-bot
- python-dotenv