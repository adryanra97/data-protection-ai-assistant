# Multi-agent AI Chatbot for Data Privacy Law

An advanced AI-powered chatbot for answering legal questions related to data privacy regulations, including GDPR, Indonesia's UU PDP, and internal company policies. Built using a multi-agent system with LangChain, Elasticsearch, Azure OpenAI, and a user-friendly web interface.

# 🔍  Overview

This chatbot uses intelligent routing and retrieval across multiple document stores to provide accurate, regulation-based answers. It supports:

Multi-agent tool selection (GDPR, UU PDP, Company Policy, Web Search)

Contextual memory for ongoing conversations

Summarized and sourced legal answers

Web UI for chat, document upload, and more

### 🧠 Multi-Agent Architecture Flow

Each stage of the chatbot leverages a different specialized agent:

### 🔎 Query Router AgentDecides which tools are most relevant for the query (e.g., ['gdpr', 'pdp']).

Role: Smart selector based on user intent.

### 📄 Retriever Agents (GDPR, PDP, Company)Each document group has a retrieval agent backed by Elasticsearch and LangChain.

Role: Extract chunks directly from relevant sources.

### 🌐 Web Search Agent (Tavily)Provides fallback answers via external search when internal data is lacking.

Role: Last-resort knowledge gatherer.

### 📚 Summarizer AgentUses Azure OpenAI to synthesize a final response based on retrieved data.

Role: Legal expert summarizer with citations.

### 💬 Memory AgentMaintains chat context using LangChain memory.

Role: Chat continuity and personalization.

### 🧠 Final Answer Agent

Integrates all inputs and decides whether to fallback to GPT-4o.
Role: Response decider + final generator.

# 🧠 Core Technologies

LangChain: Multi-agent architecture, document loading, memory, retrieval

Azure OpenAI: ChatGPT and embedding models

Elasticsearch: Semantic document store for regulations

Gradio: Beautiful legal-themed web interface with chat + file upload

FastAPI: Robust API backend for question answering

Tavily API: External fallback search engine

# 🚀 Features

📚 Multi-Document Retrieval: GDPR, UU PDP, Company Policies

🤖 Multi-Agent Tool Routing: Intelligent selection of relevant tools per query

🧠 Chat Memory: Maintains context across multiple queries

📝 Cited Summarization: Clear and well-sourced legal responses

🌐 Fallback to Web: When documents don’t contain enough information

🖥️ Web UI: Upload documents, reset memory, and chat seamlessly

# 📁 Project Structure

├── app/
│   ├── config.py          # Loads .env and settings via Pydantic
│   ├── core.py            # Elasticsearch, embeddings, store init
│   ├── ingest.py          # Document splitting and loading
│   ├── tools.py           # Multi-agent tools and Tavily API
│   ├── memory.py          # Conversational memory manager
│   ├── agent.py           # Tool router and response generator
│   └── main.py            # FastAPI app + entrypoint
├── ui/
│   └── interface.py       # Gradio-powered web interface
├── data/                  # Local folder for CSV documents (ignored)
├── .env                   # API keys and config (ignored)
├── requirements.txt       # All dependencies
├── Dockerfile             # Containerized deployment for API
├── docker-compose.yml     # Multi-container deployment (API + UI)
└── README.md

Note for Contributors:

The data/ folder is where you place regulation files in .csv format (e.g., data/gdpr/*.csv).

The .env file holds all required secrets. Use .env.example as a template.

If you're deploying or extending this project:

Make sure your documents are inside the data/ folder structured like data/gdpr, data/pdp, data/company.

Use .env to configure OpenAI, Elasticsearch, Tavily keys.

# 📌 How to Use

1. Clone & Setup

git clone https://github.com/yourname/yourrepo.git
cd yourrepo
cp .env.example .env  # Fill in your API keys

2. Run Locally

#Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#Start backend API
python app/main.py

#Start web UI
python ui/interface.py

3. Run with Docker Compose

#Build and run both API and UI
docker-compose up --build

This starts:

FastAPI API on localhost:8000

Gradio UI on localhost:7860

✅ Advantages

✅ Legally accurate and regulation-based responses

✅ Memory-aware responses for natural conversation

✅ Extensible for more policies, tools, or jurisdictions

✅ Secure: API keys via .env, Docker-ready, modular architecture

# 📬 API Example

POST /query
Content-Type: application/json
{
  "query": "Apa itu hak subjek data dalam GDPR?"
}

Returns a detailed, memory-aware, legally referenced answer.

# 👨‍⚖️ For LegalTech & Compliance Teams

This project is ideal for organizations handling legal compliance, policy inquiries, or internal data governance. Built for clarity, modularity, and scalability.

# 📄 License

MIT License

# 📢 Acknowledgements

OpenAI (Azure), LangChain, Tavily

GDPR, UU PDP, and legal data sources used in demo
