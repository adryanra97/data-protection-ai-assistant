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

### 🔎 Query Router Agent

Decides which tools are most relevant for the query (e.g., ['gdpr', 'pdp']).

Role: Smart selector based on user intent.

### 📄 Retriever Agents (GDPR, PDP, Company)

Each document group has a retrieval agent backed by Elasticsearch and LangChain.

Role: Extract chunks directly from relevant sources.

### 🌐 Web Search Agent (Tavily)

Provides fallback answers via external search when internal data is lacking.

Role: Last-resort knowledge gatherer.

### 📚 Summarizer Agent

Uses Azure OpenAI to synthesize a final response based on retrieved data.

Role: Legal expert summarizer with citations.

### 💬 Memory Agent

Maintains chat context using LangChain memory.

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

# Note for Contributors:

The data/ folder is where you place regulation files in .csv format (e.g., data/gdpr/*.csv).

The .env file holds all required secrets. Use .env.example as a template.

If you're deploying or extending this project:

Make sure your documents are inside the data/ folder structured like data/gdpr, data/pdp, data/company.

Use .env to configure OpenAI, Elasticsearch, Tavily keys.

# 📌 How to Use

1. Clone & Setup

git clone https://github.com/adryanra97/data-protection-ai-assistant

2. Run Locally

#Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#Start backend API
python main.py

#Start web UI
python ui.py

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

# 💡 Example Query
User Input:

Saya ingin mengetahui apa saja hak saya jika data saya digunakan untuk pemrosesan data dalam berbagai sumber hukum?
What Happens Internally:

🔎 Query Router Agent detects keywords like "hak", "pemrosesan data", "sumber hukum" → routes to gdpr, pdp, and company tools.

📄 Retriever Agents fetch relevant sections from GDPR, UU PDP, and internal policies.

🌐 Web Search Agent optionally supplements if documents lack certain details.

📚 Summarizer Agent synthesizes a concise legal explanation with references.

💬 Memory Agent links the query to previous conversation context if needed.

🧠 Final Answer Agent reviews and finalizes a human-like, sourced response.

Bot Output (Example):

Berdasarkan GDPR dan UU PDP, Anda memiliki hak-hak seperti: hak untuk diberi tahu, hak akses, hak untuk memperbaiki data, hak untuk dihapuskan, dan hak untuk membatasi pemrosesan. Misalnya, Pasal 13 GDPR mengharuskan pengendali data memberi informasi pada saat data dikumpulkan. Dalam konteks kebijakan internal, hak Anda juga diatur dalam kebijakan privasi perusahaan. [Sumber: GDPR Art.13, UU PDP Pasal 6]

# 👨‍⚖️ For LegalTech & Compliance Teams

This project is ideal for organizations handling legal compliance, policy inquiries, or internal data governance. Built for clarity, modularity, and scalability.

# 📄 License

MIT License

# 📢 Acknowledgements

OpenAI (Azure), LangChain, Tavily

GDPR, UU PDP, and legal data sources used in demo
