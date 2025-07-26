# 🤖 Data Protection AI Assistant

**Author: Adryan R A**

A professional, enterprise-grade AI assistant for legal question answering focused on data privacy laws including GDPR, Indonesia's UU PDP, and company policies. Built with cutting-edge AI technology and software engineering best practices.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

---

## Table of Contents

- [What This Application Does](#what-this-application-does)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start Guide](#quick-start-guide)
- [Project Structure](#project-structure)
- [Installation Options](#installation-options)
- [Configuration](#configuration)
- [How to Use](#how-to-use)
- [Document Management](#document-management)
- [Testing](#testing)
- [Security](#security)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## What This Application Does

The **Data Protection AI Assistant** is an intelligent legal advisor that helps individuals and organizations understand and comply with data protection laws. It combines advanced AI technology with comprehensive legal knowledge to provide:

### **For Legal Professionals**
- Instant access to GDPR, UU PDP, and company policy information
- Source-backed legal guidance with citations
- Document analysis and compliance checking
- Multi-jurisdictional legal comparisons

### **For Businesses**
- Data protection compliance guidance
- Privacy policy review and recommendations
- Breach response procedures
- Employee training on data protection

### **For Students & Researchers**
- Educational resource for data protection law
- Comparative legal analysis
- Research assistance with academic citations
- Interactive learning through Q&A

### **For General Users**
- Understanding personal data rights
- GDPR and UU PDP guidance in plain language
- Privacy-related question answering
- Document upload for personalized advice

---

## Key Features

### **Advanced AI Intelligence**
- **Multi-Agent Architecture**: Specialized AI agents for different legal domains
- **Smart Query Routing**: Automatically selects the best tools for each question
- **Contextual Memory**: Maintains conversation history for follow-up questions
- **Source Citations**: All answers include references to legal documents

### **Powerful Search & Retrieval**
- **Elasticsearch Integration**: Lightning-fast semantic search across legal documents
- **Vector Embeddings**: Advanced similarity matching for relevant content discovery
- **Multi-Document Support**: Simultaneous search across GDPR, UU PDP, and company policies
- **Intelligent Chunking**: Optimized text segmentation for accurate retrieval

### **Document Management**
- **File Upload Support**: CSV, TXT, XLSX, and PDF document processing
- **Automatic Processing**: Documents are automatically chunked and indexed
- **Document Control**: Activate/deactivate documents for targeted searches
- **Metadata Management**: Rich document information and categorization

### **Professional Web Interface**
- **Intuitive Chat Interface**: Clean, responsive design for natural conversations
- **Tabbed Navigation**: Separate sections for chat and document management
- **Real-time Processing**: Live updates and streaming responses
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile

### **Enterprise-Ready Backend**
- **FastAPI Framework**: High-performance, production-ready API
- **Async Processing**: Non-blocking request handling for scalability
- **OpenAPI Documentation**: Auto-generated API documentation
- **Health Monitoring**: Built-in health checks and monitoring endpoints

### **Security & Reliability**
- **Input Validation**: Comprehensive data validation using Pydantic models
- **Error Handling**: Robust error handling with detailed logging
- **Environment Configuration**: Secure credential management
- **Audit Logging**: Complete request and response logging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Gradio Web UI │   FastAPI Docs  │   Mobile/API Clients        │
│   Port: 7860    │   Port: 8000    │   REST API Access          │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                ┌───────────────▼───────────────┐
                │         FastAPI Backend        │
                │    (API Endpoints & Logic)     │
                └───────────────┬───────────────┘
                                │
                ┌───────────────▼───────────────┐
                │      Multi-Agent QA Engine     │
                │   (Query Routing & Synthesis)   │
                └───────────────┬───────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
┌───▼────┐              ┌──────▼──────┐              ┌─────▼─────┐
│ GDPR   │              │  Document   │              │  Web      │
│ Agent  │              │  Manager    │              │  Search   │
└───┬────┘              └──────┬──────┘              └─────┬─────┘
    │                          │                          │
┌───▼────┐              ┌──────▼──────┐              ┌─────▼─────┐
│ UU PDP │              │ Elasticsearch│              │  Tavily   │
│ Agent  │              │   Storage    │              │   API     │
└───┬────┘              └─────────────┘              └───────────┘
    │                          
┌───▼────┐                     
│Company │                     
│Policy  │                     
│ Agent  │                     
└────────┘                     
```

### **Data Flow**
1. **User Input**: Question submitted via web interface or API
2. **Query Analysis**: AI router analyzes intent and selects appropriate tools
3. **Document Search**: Relevant legal documents retrieved from Elasticsearch
4. **Answer Synthesis**: AI synthesizes response with citations
5. **Response Delivery**: Formatted answer returned to user interface

---

## Quick Start Guide

### **Prerequisites**
- **Python 3.11+** (Python 3.9+ supported)
- **Git** (for cloning the repository)
- **Docker & Docker Compose** (recommended for easy deployment)
- **API Keys**: OpenAI/Azure OpenAI, Tavily (see configuration section)

### **One-Command Setup**

```bash
# Clone the repository
git clone https://github.com/adryanra97/data-protection-ai-assistant.git
cd data-protection-ai-assistant

# Run the automated setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Check system requirements
2. Create virtual environment
3. Install all dependencies
4. Set up configuration files
5. Create necessary directories
6. Start Elasticsearch (if Docker available)
7. Test the installation

---

## Project Structure

```
data-protection-ai-assistant/
├── src/                          # Source code
│   ├── agents/                   # AI agents and tools
│   │   ├── qa_engine.py         # Main QA orchestrator
│   │   └── tools.py             # Document retrieval tools
│   ├── api/                     # FastAPI application
│   │   ├── main.py              # API endpoints
│   │   └── models.py            # Pydantic request/response models
│   ├── core/                    # Core configuration
│   │   └── config.py            # Settings management
│   ├── services/                # Business logic services
│   │   ├── search_engine.py     # Elasticsearch service
│   │   ├── ingestion.py         # Document ingestion
│   │   └── document_manager.py  # Document lifecycle management
│   ├── ui/                      # User interface
│   │   └── gradio_app.py        # Web interface
│   └── utils/                   # Utility functions
│       ├── document_processor.py # Text processing utilities
│       └── logging_config.py    # Logging configuration
├── tests/                       # Test suites
│   ├── test_api.py              # API endpoint tests
│   ├── test_agents.py           # Agent functionality tests
│   └── test_document_manager.py # Document management tests
├── data/                        # Legal documents storage
│   ├── gdpr/                    # GDPR documents (CSV format)
│   ├── uupdp/                   # Indonesia UU PDP documents
│   └── company/                 # Company policy documents
├── docs/                        # Documentation
│   ├── DOCUMENT_MANAGEMENT.md   # Document management guide
│   └── API_REFERENCE.md         # Complete API documentation
├── logs/                        # Application logs
├── main.py                      # Application entry point
├── setup.sh                     # Automated setup script
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker configuration
├── Dockerfile                   # Container definition
├── .env.template               # Environment variables template
└── test_document_management.py  # Integration test script
```

---

## Installation Options

### **Option 1: Docker Deployment (Recommended)**

**Best for: Production deployment, quick testing, users who want everything configured automatically**

```bash
# Clone repository
git clone https://github.com/adryanra97/data-protection-ai-assistant.git
cd data-protection-ai-assistant

# Copy and configure environment
cp .env.template .env
# Edit .env with your API keys (see Configuration section)

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**What this includes:**
- Web application (port 7860)
- API backend (port 8000)
- Elasticsearch (port 9200)
- Automatic service orchestration
- Health monitoring

### **Option 2: Local Development Setup**

**Best for: Developers, customization, learning the codebase**

```bash
# Clone repository
git clone https://github.com/adryanra97/data-protection-ai-assistant.git
cd data-protection-ai-assistant

# Use automated setup
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your configuration

# Start Elasticsearch separately (if not using Docker)
# Option A: Docker
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

# Option B: Local installation
# Download from https://www.elastic.co/downloads/elasticsearch

# Run the application
python main.py --both  # Starts both API and UI
# Or separately:
# python main.py --api   # API only
# python main.py --ui    # UI only
```

### **Option 3: Component-by-Component**

**Best for: Advanced users, custom integrations, microservices deployment**

```bash
# Terminal 1: Start Elasticsearch
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

# Terminal 2: Start API Backend
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Start Web Interface
python -c "from src.ui.gradio_app import launch_interface; launch_interface()"

# Terminal 4: Run tests
pytest tests/ -v
```

---

## Configuration

### **Environment Variables**

Copy `.env.template` to `.env` and configure the following:

#### **AI Configuration**
```bash
# OpenAI Configuration (Option 1)
OPENAI_CHAT_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBED_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4
OPENAI_EMBED_MODEL=text-embedding-ada-002

# Azure OpenAI Configuration (Option 2 - Alternative to OpenAI)
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4-deployment-name
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-deployment-name
```

#### **Search Configuration**
```bash
# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic  # If using authentication
ELASTICSEARCH_PASSWORD=your-password  # If using authentication

# Tavily API (for web search fallback)
TAVILY_API_KEY=tvly-your-tavily-api-key-here
```

#### **Application Settings**
```bash
# Server Configuration
API_HOST=localhost
API_PORT=8000
UI_HOST=localhost
UI_PORT=7860

# Logging and Debug
DEBUG=false  # Set to true for development
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Search Parameters
SEARCH_K=5  # Number of documents to retrieve
SEARCH_SCORE_THRESHOLD=0.5  # Minimum relevance score
MAX_CHUNK_SIZE=1000  # Document chunk size
CHUNK_OVERLAP=200  # Overlap between chunks
```

### **Getting API Keys**

#### **OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key and add to your `.env` file

#### **Tavily API Key**
1. Visit [Tavily](https://tavily.com/)
2. Sign up for an account
3. Navigate to your dashboard
4. Copy your API key
5. Add to your `.env` file

#### **Azure OpenAI (Alternative)**
1. Create an Azure account and set up Azure OpenAI
2. Deploy GPT-4 and text-embedding models
3. Get your endpoint, API key, and deployment names
4. Configure in `.env` file

---

## How to Use

### **Web Interface Usage**

1. **Access the Application**
   ```bash
   # Open your browser and navigate to:
   http://localhost:7860
   ```

2. **Chat Tab - Ask Legal Questions**
   - Type your question in the chat box
   - Get comprehensive answers with source citations
   - Ask follow-up questions for clarification
   - Use the "Reset Chat" button to start a new conversation

   **Example Questions:**
   ```
    "What are the main principles of GDPR data processing?"
    "How does UU PDP differ from GDPR regarding consent?"
    "What steps should a company take after a data breach?"
    "What are the penalties for GDPR violations?"
    "Explain the right to be forgotten under GDPR"
   ```

3. **Document Management Tab**
   - Upload legal documents (PDF, TXT, CSV, XLSX)
   - Manage document library with activate/deactivate controls
   - View all uploaded documents with metadata
   - Delete documents when no longer needed

### **API Usage**

#### **Ask a Legal Question**
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What are the penalties for GDPR violations?",
       "conversation_id": "user_session_123"
     }'
```

#### **Upload a Document**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@legal_document.pdf" \
     -F "title=Company Privacy Policy" \
     -F "description=Updated privacy policy for 2024" \
     -F "category=company_policy"
```

#### **List Documents**
```bash
curl -X GET "http://localhost:8000/documents"
```

#### **Health Check**
```bash
curl -X GET "http://localhost:8000/health"
```

### **API Documentation**

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## Document Management

The application includes a powerful document management system that allows you to:

### **Upload Documents**
- **Supported Formats**: PDF, TXT, CSV, XLSX
- **Automatic Processing**: Documents are automatically chunked and indexed
- **Metadata Support**: Add titles, descriptions, and categories
- **Instant Availability**: Documents become searchable immediately after upload

### **Manage Document Library**
- **View All Documents**: See complete list with metadata
- **Filter by Category**: Organize documents by type (GDPR, UU PDP, company policies)
- **Activation Control**: Enable/disable documents for searches
- **Delete Functionality**: Remove unwanted documents

### **Document Categories**
- `gdpr` - GDPR-related documents
- `uupdp` - Indonesia UU PDP documents
- `company_policy` - Company policy documents
- `legal_doc` - General legal documents
- `user_upload` - User-uploaded content (default)

For detailed document management instructions, see [docs/DOCUMENT_MANAGEMENT.md](docs/DOCUMENT_MANAGEMENT.md).

---

## Testing

### **Running Tests**

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_document_manager.py -v

# Run integration tests
python test_document_management.py
```

### **Test Categories**

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Document Processing Tests**: File upload and processing validation
- **Agent Tests**: AI agent functionality verification

### **Test Coverage**

The project maintains high test coverage across:
- API endpoints and request/response handling
- Document processing and chunking
- Search engine integration
- AI agent functionality
- Configuration management

---

## Security

### **Security Features**

- **Input Validation**: All inputs validated using Pydantic models
- **API Key Protection**: Sensitive credentials stored in environment variables
- **Error Handling**: Detailed errors logged but sanitized for users
- **File Upload Security**: File type and size validation
- **CORS Configuration**: Configurable cross-origin resource sharing

### **Best Practices**

```bash
# Use strong API keys
OPENAI_API_KEY=sk-very-long-and-complex-key-here

# Restrict CORS in production
CORS_ORIGINS=["https://yourdomain.com"]

# Use HTTPS in production
API_HOST=0.0.0.0  # Only for development
USE_SSL=true  # For production

# Regular security updates
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### **Security Considerations for Production**

1. **Environment Variables**: Never commit API keys to version control
2. **Network Security**: Use VPN or private networks for Elasticsearch
3. **Authentication**: Implement user authentication for production use
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Monitoring**: Set up security monitoring and alerting

---

## Deployment

### **Production Deployment Options**

#### **Option 1: Docker with Docker Compose**
```bash
# Production docker-compose configuration
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "7860:7860"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

#### **Option 2: Kubernetes**
```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-protection-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-protection-ai
  template:
    metadata:
      labels:
        app: data-protection-ai
    spec:
      containers:
      - name: app
        image: your-registry/data-protection-ai:latest
        ports:
        - containerPort: 8000
        - containerPort: 7860
```

#### **Option 3: Cloud Platforms**

**AWS Deployment:**
```bash
# Using AWS ECS or EKS
aws ecr create-repository --repository-name data-protection-ai
docker build -t data-protection-ai .
docker tag data-protection-ai:latest YOUR_ECR_URI:latest
docker push YOUR_ECR_URI:latest
```

**Google Cloud:**
```bash
# Using Google Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/data-protection-ai
gcloud run deploy --image gcr.io/PROJECT_ID/data-protection-ai --platform managed
```

**Azure:**
```bash
# Using Azure Container Instances
az container create --resource-group myResourceGroup \
  --name data-protection-ai --image YOUR_REGISTRY/data-protection-ai:latest
```

### **Monitoring & Observability**

```bash
# Health monitoring
curl http://localhost:8000/health

# Application metrics
curl http://localhost:8000/stats

# Log monitoring
tail -f logs/app.log | grep ERROR
```

---

## Troubleshooting

### **Common Issues & Solutions**

#### **1. Elasticsearch Connection Issues**
```bash
# Problem: Cannot connect to Elasticsearch
# Solution: Check if Elasticsearch is running
curl http://localhost:9200/_cluster/health

# If not running, start with Docker:
docker run -d --name elasticsearch -p 9200:9200 \
  -e "discovery.type=single-node" elasticsearch:8.11.0

# Check Docker logs:
docker logs elasticsearch
```

#### **2. API Key Issues**
```bash
# Problem: OpenAI API key errors
# Solution: Verify your API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Check your .env file:
cat .env | grep OPENAI_API_KEY
```

#### **3. Python Import Errors**
```bash
# Problem: Module not found errors
# Solution: Check Python path and virtual environment
echo $PYTHONPATH
which python

# Activate virtual environment:
source venv/bin/activate

# Reinstall dependencies:
pip install -r requirements.txt
```

#### **4. Port Already in Use**
```bash
# Problem: Port 8000 or 7860 already in use
# Solution: Find and kill the process
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9

# Or use different ports:
python main.py --api --port 8001
```

#### **5. Docker Issues**
```bash
# Problem: Docker containers not starting
# Solution: Check Docker daemon and logs
docker ps -a
docker-compose logs

# Restart Docker services:
docker-compose down
docker-compose up -d

# Rebuild containers:
docker-compose build --no-cache
```

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
# Set in .env file:
DEBUG=true
LOG_LEVEL=DEBUG

# Or run with debug flag:
python main.py --both --debug --log-file logs/debug.log

# View debug logs:
tail -f logs/debug.log
```

### **Getting Help**

1. **Check the logs**: Always check `logs/app.log` for error messages
2. **Test individual components**: Use the API endpoints to isolate issues
3. **Run the test suite**: `pytest tests/` to verify system functionality
4. **Check system resources**: Ensure adequate memory and disk space
5. **Verify network connectivity**: Test API keys and external service access

---

## Contributing

We welcome contributions from developers, legal professionals, and users!

### **Development Setup**

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/data-protection-ai-assistant.git
cd data-protection-ai-assistant

# Set up development environment
./setup.sh --dev

# Create a feature branch
git checkout -b feature/amazing-new-feature

# Make your changes and test
pytest tests/
python test_document_management.py

# Commit and push
git commit -m "Add amazing new feature"
git push origin feature/amazing-new-feature
```

### **Contribution Guidelines**

1. **Code Style**: Follow PEP 8 and include type hints
2. **Documentation**: Update docstrings and README for new features
3. **Testing**: Add tests for new functionality
4. **Attribution**: Add "Author: Your Name" to new files
5. **Legal Content**: Ensure legal accuracy for law-related changes

### **Areas for Contribution**

- **Legal Content**: Additional jurisdictions and legal documents
- **UI/UX**: Interface improvements and new features
- **AI Agents**: Enhanced agent capabilities and new tools
- **Documentation**: Tutorials, guides, and API documentation
- **Testing**: Additional test coverage and integration tests
- **Internationalization**: Multi-language support

### **Recognition**

All contributors will be recognized in the project documentation and release notes.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact & Support

**Author: Adryan R A**
- **GitHub**: [@adryanra97](https://github.com/adryanra97)
- **Project Repository**: [data-protection-ai-assistant](https://github.com/adryanra97/data-protection-ai-assistant)

## Acknowledgments

Special thanks to the following technologies and communities:

- **[LangChain](https://langchain.com/)** - For the powerful AI framework and tools
- **[FastAPI](https://fastapi.tiangolo.com/)** - For the high-performance web framework
- **[Gradio](https://gradio.app/)** - For the intuitive UI components
- **[Elasticsearch](https://www.elastic.co/)** - For powerful search capabilities
- **[OpenAI](https://openai.com/)** - For advanced language models
- **[Tavily](https://tavily.com/)** - For web search integration

---

<div align="center">

### **Ready to Get Started?**

```bash
git clone https://github.com/adryanra97/data-protection-ai-assistant.git
cd data-protection-ai-assistant
./setup.sh
```

** Star this project if you find it useful!**

---

<strong> Legal Disclaimer</strong><br>
<em>This application is for educational and informational purposes only. 
Always consult with qualified legal professionals for specific legal advice.</em>

---

<small>
Built for Legal Technology Innovation<br>
© 2024 Adryan R A. All rights reserved.
</small>

</div>
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
