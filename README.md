# Domifile

Domifile is an AI-powered **organizational memory system for Homeowners Associations (HOAs)**.

It connects to an HOA's Google Drive document archive and allows board members to ask natural-language questions about their documents. Domifile analyzes the documents, retrieves relevant information, and produces answers with citations to the source files.

The long-term vision is an **operational knowledge layer for HOA governance**: contracts, vendors, maintenance history, governing documents, and institutional memory.

---

# Why Domifile Exists

Volunteer HOA boards face recurring problems:

* Institutional knowledge is lost when board members rotate off.
* Important documents are buried in Google Drive folders or email, or worse, in a pile of paper.
* Contracts, vendor relationships, and maintenance history become unclear.
* Governing documents are difficult to search during meetings.

Domifile addresses this by turning an HOA’s document archive into a **searchable knowledge base**.

Example question:

> When was the irrigation system replaced?

Example answer:

* Irrigation system replacement occurred in May 2018
* Vendor: GreenScape Irrigation
* Sources: `irrigation_contract_2018.pdf`, `minutes_2018_06.pdf`

---

# Milestone 1 – HOA Document Brain

The first milestone focuses on proving the core value proposition:

**Ask questions about HOA documents and receive answers with citations.**

Pipeline:

Google Drive → Document ingestion → Text extraction → Chunking → Embeddings → Retrieval → AI answer generation

Features in Milestone 1:

* Connect to a Google Drive folder
* Ingest and index HOA documents
* Retrieve relevant document chunks
* Generate answers with cited sources
* Minimal chat interface

No structured entity extraction or workflow automation yet.

---

# Architecture Overview

Domifile uses a simple Retrieval-Augmented Generation (RAG) architecture.

Components:

1. **Drive Connector**

   * Lists and downloads files from a selected Google Drive folder.

2. **Document Ingestion**

   * Extracts text from supported document formats.

3. **Chunking**

   * Splits documents into manageable sections for retrieval.

4. **Embeddings**

   * Converts chunks into vector embeddings for semantic search.

5. **Vector Retrieval**

   * Searches for document chunks relevant to a question.

6. **Query Planner**

   * Expands user questions into multiple search queries.

7. **Answer Generation**

   * Uses an LLM to synthesize answers from retrieved evidence.

---

# Technology Stack

Backend

* Python
* Flask or FastAPI
* PostgreSQL
* pgvector

Libraries

* google-api-python-client
* pdfminer.six
* python-docx

LLM Providers

* Google Gemini
* OpenAI

---

# Repository Structure

Suggested structure:

domifile/
drive/      # Google Drive integration
ingest/     # document extraction + chunking
rag/        # embeddings, retrieval, query planner
api/        # HTTP endpoints
ui/         # minimal chat interface

---

# Example Questions

Domifile should be able to answer questions such as:

* Who handles landscaping?
* When was the irrigation system replaced?
* What do the bylaws say about pets?
* When was the pool resurfaced?
* What insurance policies exist?

---

# Future Direction

Later milestones will add:

* Entity extraction (vendors, contracts, maintenance events)
* HOA knowledge graph
* Automatic maintenance timeline
* Vendor registry
* Governing document interpretation
* Workflow automation for board operations

Ultimately Domifile becomes the **institutional memory system for HOAs**.

---

# Status

Domifile is currently in early development.

Milestone 1 goal: demonstrate that AI can reliably answer HOA questions using the organization's existing document archive.

---

# License

TBD

---

# Getting Started

```
  brew install uv
  uv venv
  source .venv/bin/activate
  uv pip install -e .
```
