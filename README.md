# 🤖 Data Protection AI Assistant

**Author: Adryan R A**

An advanced multi-agent AI system for legal question answering focused on data privacy laws including GDPR, Indonesia's UU PDP, and company policies. Built with professional software engineering practices and enterprise-ready architecture.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)

## Features

### Multi-Agent Intelligence
- **Query Router Agent**: Smart tool selection based on user intent
- **Document Retrieval Agents**: Specialized agents for GDPR, UU PDP, and company policies
- **Web Search Agent**: Fallback search using Tavily for recent legal developments
- **Synthesis Agent**: Expert legal summarization with source citations
- **Memory Agent**: Conversation context management

### Advanced Search & Retrieval
- **Elasticsearch Integration**: High-performance document search with vector embeddings
- **Azure OpenAI Embeddings**: Semantic similarity search
- **Smart Document Chunking**: Context-preserving text segmentation
- **Relevance Scoring**: Intelligent filtering of search results

### Professional API & UI
- **FastAPI Backend**: Production-ready REST API with OpenAPI documentation
- **Gradio Web Interface**: User-friendly chat interface with document upload
- **Real-time Processing**: Async request handling and streaming responses
- **Health Monitoring**: Comprehensive system health checks

### Enterprise Features
- **Docker Containerization**: Easy deployment and scaling
- **Comprehensive Logging**: Structured logging with configurable levels
- **Configuration Management**: Environment-based configuration with validation
- **Error Handling**: Robust error handling with detailed error responses
- **Testing Suite**: Unit and integration tests

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   FastAPI       │    │  Elasticsearch  │
│   Port: 7860    │◄──►│   Port: 8000    │◄──►│   Port: 9200    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   Multi-Agent       │
                    │   QA Engine         │
                    └─────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │  GDPR Tool  │ │  PDP Tool   │ │ Tavily Tool │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## Project Structure

```
data-protection-ai-assistant/
├── src/                          # Source code
│   ├── agents/                   # AI agents and tools
│   │   ├── qa_engine.py         # Main QA orchestrator
│   │   └── tools.py             # Document retrieval tools
│   ├── api/                     # FastAPI application
│   │   ├── main.py              # API endpoints
│   │   └── models.py            # Pydantic models
│   ├── core/                    # Core configuration
│   │   └── config.py            # Settings management
│   ├── services/                # Business logic services
│   │   ├── search_engine.py     # Elasticsearch service
│   │   └── ingestion.py         # Document ingestion
│   ├── ui/                      # User interface
│   │   └── gradio_app.py        # Web interface
│   └── utils/                   # Utility functions
│       ├── document_processor.py # Text processing
│       └── logging_config.py    # Logging setup
├── tests/                       # Test suites
├── data/                        # Legal documents
│   ├── gdpr/                    # GDPR documents
│   ├── uupdp/                   # UU PDP documents
│   └── company/                 # Company policies
├── docs/                        # Documentation
├── logs/                        # Application logs
├── main.py                      # Application entry point
├── requirements.txt             # Dependencies
├── docker-compose.yml           # Docker configuration
├── Dockerfile                   # Container definition
└── .env.template               # Environment template
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Elasticsearch cluster (local or cloud)
- Azure OpenAI or OpenAI API access
- Tavily API key (for web search)

### 1. Clone Repository
```bash
git clone https://github.com/adryanra97/data-protection-ai-assistant.git
cd data-protection-ai-assistant
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your API keys and configuration
nano .env
```

### 3. Installation Options

#### Option A: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API only
python main.py --api

# Run UI only  
python main.py --ui

# Run both API and UI
python main.py --both

# Run with debug mode
python main.py --both --debug
```

#### Option B: Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access Applications
- **API Documentation**: http://localhost:8000/docs
- **Web Interface**: http://localhost:7860
- **Health Check**: http://localhost:8000/health
- **Elasticsearch**: http://localhost:9200

## Usage Guide

### API Endpoints

#### Ask Legal Question
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the penalties for GDPR violations?",
       "context": "optional additional context"
     }'
```

#### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -F "file=@legal_document.txt"
```

#### Reset Conversation
```bash
curl -X POST "http://localhost:8000/reset"
```

### Web Interface Usage

1. **Open Browser**: Navigate to http://localhost:7860
2. **Ask Questions**: Type legal questions in the chat interface
3. **Upload Documents**: Use the sidebar to upload relevant documents
4. **View Responses**: Get comprehensive answers with source citations
5. **Continue Conversation**: Ask follow-up questions for clarification

### Example Questions

- "What are the key principles of GDPR data processing?"
- "How does UU PDP differ from GDPR in terms of consent requirements?"
- "What steps should a company take after a data breach?"
- "What are the penalties for data protection violations in Indonesia?"
- "How should personal data be stored according to our company policy?"

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_CHAT_API_KEY` | OpenAI API key for chat models | Yes |
| `OPENAI_EMBED_API_KEY` | OpenAI API key for embeddings | Yes |
| `ELASTICSEARCH_URL` | Elasticsearch cluster URL | Yes |
| `ELASTICSEARCH_API_KEY` | Elasticsearch API key | No |
| `TAVILY_API_KEY` | Tavily API key for web search | Yes |
| `DEBUG` | Enable debug mode | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

### Application Settings

The application supports extensive configuration through environment variables:

- **Search Configuration**: Adjust search parameters like `SEARCH_K` and `SEARCH_SCORE_THRESHOLD`
- **Document Processing**: Configure `MAX_CHUNK_SIZE` for document splitting
- **API Settings**: Set `API_HOST` and `API_PORT` for server configuration
- **Logging**: Configure log levels and output destinations

## Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_document_processor.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Document Processing Tests**: Text processing validation

## Documentation

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Code Documentation
All modules include comprehensive docstrings following Google style:
- Class and function descriptions
- Parameter and return type annotations
- Usage examples and error handling
- Author attribution

## Security Considerations

- **API Keys**: Store sensitive credentials in environment variables
- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Detailed errors are logged but sanitized for users
- **CORS**: Configure CORS settings appropriately for production
- **Rate Limiting**: Consider implementing rate limiting for production use

## Deployment

### Production Deployment

For production deployment, consider:

1. **Container Orchestration**: Use Kubernetes or Docker Swarm
2. **Load Balancing**: Implement load balancer for high availability
3. **Monitoring**: Set up application and infrastructure monitoring
4. **Logging**: Configure centralized logging (ELK stack, etc.)
5. **Security**: Implement authentication, authorization, and security headers
6. **Scaling**: Configure auto-scaling based on demand

### Environment-Specific Configuration

- **Development**: Use `.env` file with debug mode enabled
- **Staging**: Use environment variables with test data
- **Production**: Use secure secret management and production data

## Contributing

1. **Fork Repository**: Create your own fork
2. **Create Branch**: `git checkout -b feature/amazing-feature`
3. **Code Standards**: Follow PEP 8 and include type hints
4. **Add Tests**: Ensure new features have test coverage
5. **Documentation**: Update docstrings and README as needed
6. **Commit Changes**: `git commit -m 'Add amazing feature'`
7. **Push Branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**: Submit PR for review

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Add author attribution to new files

## Troubleshooting

### Common Issues

#### Elasticsearch Connection Error
```bash
# Check Elasticsearch status
curl http://localhost:9200/_cluster/health

# Restart Elasticsearch
docker-compose restart elasticsearch
```

#### Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:./src"
```

#### API Timeout Issues
- Increase timeout settings in configuration
- Check Elasticsearch cluster performance
- Verify API key limits and quotas

### Debug Mode
Enable debug mode for detailed logging:
```bash
python main.py --both --debug --log-file logs/debug.log
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Adryan R A**
- GitHub: [@adryanra97](https://github.com/adryanra97)
- Email: [Contact via GitHub]

## Acknowledgments

- **LangChain**: For the AI framework and tools
- **FastAPI**: For the high-performance web framework
- **Gradio**: For the intuitive UI components
- **Elasticsearch**: For powerful search capabilities
- **OpenAI**: For advanced language models
- **Tavily**: For web search integration

---

<div align="center">
<strong>Built with for Legal Technology Innovation</strong><br>
<em>⚖️ For educational purposes - consult legal professionals for specific advice</em>
</div>

### Final Answer Agent

Integrates all inputs and decides whether to fallback to GPT-4o.
Role: Response decider + final generator.

# Core Technologies

LangChain: Multi-agent architecture, document loading, memory, retrieval

Azure OpenAI: ChatGPT and embedding models

Elasticsearch: Semantic document store for regulations

Gradio: Beautiful legal-themed web interface with chat + file upload

FastAPI: Robust API backend for question answering

Tavily API: External fallback search engine

# Features

Multi-Document Retrieval: GDPR, UU PDP, Company Policies

Multi-Agent Tool Routing: Intelligent selection of relevant tools per query

Chat Memory: Maintains context across multiple queries

Cited Summarization: Clear and well-sourced legal responses

Fallback to Web: When documents don’t contain enough information

Web UI: Upload documents, reset memory, and chat seamlessly

# Note for Contributors:

The data/ folder is where you place regulation files in .csv format (e.g., data/gdpr/*.csv).

The .env file holds all required secrets. Use .env.example as a template.

If you're deploying or extending this project:

Make sure your documents are inside the data/ folder structured like data/gdpr, data/pdp, data/company.

Use .env to configure OpenAI, Elasticsearch, Tavily keys.

# How to Use

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

Advantages

Legally accurate and regulation-based responses

Memory-aware responses for natural conversation

Extensible for more policies, tools, or jurisdictions

Secure: API keys via .env, Docker-ready, modular architecture

# API Example

POST /query
Content-Type: application/json
{
  "query": "Apa itu hak subjek data dalam GDPR?"
}

Returns a detailed, memory-aware, legally referenced answer.

# Example Query
User Input:

Saya ingin mengetahui apa saja hak saya jika data saya digunakan untuk pemrosesan data dalam berbagai sumber hukum?
What Happens Internally:

Query Router Agent detects keywords like "hak", "pemrosesan data", "sumber hukum" → routes to gdpr, pdp, and company tools.

Retriever Agents fetch relevant sections from GDPR, UU PDP, and internal policies.

Web Search Agent optionally supplements if documents lack certain details.

Summarizer Agent synthesizes a concise legal explanation with references.

Memory Agent links the query to previous conversation context if needed.

Final Answer Agent reviews and finalizes a human-like, sourced response.

Bot Output (Example):

Berdasarkan GDPR dan UU PDP, Anda memiliki hak-hak seperti: hak untuk diberi tahu, hak akses, hak untuk memperbaiki data, hak untuk dihapuskan, dan hak untuk membatasi pemrosesan. Misalnya, Pasal 13 GDPR mengharuskan pengendali data memberi informasi pada saat data dikumpulkan. Dalam konteks kebijakan internal, hak Anda juga diatur dalam kebijakan privasi perusahaan. [Sumber: GDPR Art.13, UU PDP Pasal 6]

# For LegalTech & Compliance Teams

This project is ideal for organizations handling legal compliance, policy inquiries, or internal data governance. Built for clarity, modularity, and scalability.

# License

MIT License

# Acknowledgements

OpenAI (Azure), LangChain, Tavily

GDPR, UU PDP, and legal data sources used in demo
