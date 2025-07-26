#!/bin/bash

#######################################
# Data Protection AI Assistant Setup Script
# Author: Adryan R A
# 
# This comprehensive setup script automates the installation and configuration
# of the Data Protection AI Assistant. It supports multiple deployment options
# and provides detailed guidance for both developers and end users.
#######################################

set -e  # Exit on any error

# Script version and configuration
SCRIPT_VERSION="2.0.0"
PROJECT_NAME="Data Protection AI Assistant"
PYTHON_MIN_VERSION="3.9"
REQUIRED_DISK_SPACE_MB=2048

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global flags
SKIP_DOCKER=false
SKIP_ES=false
DEV_MODE=false
VERBOSE=false
AUTO_START=false

#######################################
# Print functions with enhanced formatting
#######################################
print_banner() {
    echo
    print_color $BLUE "╔══════════════════════════════════════════════════════════════╗"
    print_color $BLUE "║                                                              ║"
    print_color $BLUE "║    🤖 Data Protection AI Assistant Setup v$SCRIPT_VERSION            ║"
    print_color $BLUE "║    Author: Adryan R A                                        ║"
    print_color $BLUE "║                                                              ║"
    print_color $BLUE "╚══════════════════════════════════════════════════════════════╝"
    echo
}

print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    print_color $CYAN "📋 =================================="
    print_color $CYAN "📋 $1"
    print_color $CYAN "📋 =================================="
    echo
}

print_step() {
    print_color $GREEN "✅ $1"
}

print_substep() {
    print_color $WHITE "   → $1"
}

print_warning() {
    print_color $YELLOW "⚠️  $1"
}

print_error() {
    print_color $RED "❌ $1"
}

print_info() {
    print_color $BLUE "ℹ️  $1"
}

print_success() {
    print_color $GREEN "🎉 $1"
}

#######################################
# Utility functions
#######################################
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

get_os() {
    case "$OSTYPE" in
        linux*)   echo "linux" ;;
        darwin*)  echo "macos" ;;
        msys*)    echo "windows" ;;
        cygwin*)  echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

get_available_space_mb() {
    if [[ "$(get_os)" == "macos" ]]; then
        df -m . | awk 'NR==2{print $4}'
    else
        df -m . | awk 'NR==2{print $4}'
    fi
}

prompt_user() {
    local message=$1
    local default=$2
    local response
    
    read -p "$(print_color $YELLOW "❓ $message") ${default:+[$default] }" response
    echo "${response:-$default}"
}

confirm_action() {
    local message=$1
    local response
    
    read -p "$(print_color $YELLOW "❓ $message (y/n): ")" -n 1 -r response
    echo
    [[ $response =~ ^[Yy]$ ]]
}

#######################################
# System requirement checks
#######################################
check_system_requirements() {
    print_header "System Requirements Check"
    
    # Check operating system
    local os=$(get_os)
    print_step "Operating System: $os"
    
    # Check available disk space
    local available_space=$(get_available_space_mb)
    if [ "$available_space" -lt $REQUIRED_DISK_SPACE_MB ]; then
        print_warning "Low disk space: ${available_space}MB available, ${REQUIRED_DISK_SPACE_MB}MB recommended"
    else
        print_step "Disk space: ${available_space}MB available"
    fi
    
    # Check internet connectivity
    if ping -c 1 google.com >/dev/null 2>&1; then
        print_step "Internet connectivity: Available"
    else
        print_warning "Internet connectivity: Limited or unavailable"
        print_info "Some features may not work without internet access"
    fi
}

check_python_version() {
    print_header "Python Environment Check"
    
    local python_cmd=""
    local python_version=""
    
    # Find Python executable
    if command_exists python3; then
        python_cmd="python3"
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
    elif command_exists python; then
        python_cmd="python"
        python_version=$(python --version 2>&1 | awk '{print $2}')
    else
        print_error "Python is not installed!"
        print_info "Please install Python $PYTHON_MIN_VERSION or higher from https://python.org"
        exit 1
    fi
    
    # Check version compatibility
    local version_major=$(echo $python_version | cut -d. -f1)
    local version_minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$version_major" -lt 3 ] || ([ "$version_major" -eq 3 ] && [ "$version_minor" -lt 9 ]); then
        print_error "Python $python_version is installed, but Python $PYTHON_MIN_VERSION+ is required"
        print_info "Please upgrade Python to version $PYTHON_MIN_VERSION or higher"
        exit 1
    fi
    
    print_step "Python $python_version detected at $(which $python_cmd)"
    
    # Check pip availability
    if ! command_exists pip && ! command_exists pip3; then
        print_error "pip is not installed!"
        print_info "Please install pip: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi
    
    local pip_cmd="pip"
    if command_exists pip3; then
        pip_cmd="pip3"
    fi
    
    print_step "pip available at $(which $pip_cmd)"
    
    # Export for use in other functions
    export PYTHON_CMD=$python_cmd
    export PIP_CMD=$pip_cmd
}

check_docker_availability() {
    print_header "Docker Availability Check"
    
    if [ "$SKIP_DOCKER" = true ]; then
        print_info "Docker check skipped by user request"
        export DOCKER_AVAILABLE=false
        export DOCKER_COMPOSE_AVAILABLE=false
        return
    fi
    
    # Check Docker
    if command_exists docker; then
        if docker info >/dev/null 2>&1; then
            print_step "Docker is installed and running"
            export DOCKER_AVAILABLE=true
            
            # Check Docker Compose
            if command_exists docker-compose; then
                print_step "Docker Compose is available (standalone)"
                export DOCKER_COMPOSE_AVAILABLE=true
                export DOCKER_COMPOSE_CMD="docker-compose"
            elif docker compose version >/dev/null 2>&1; then
                print_step "Docker Compose is available (plugin)"
                export DOCKER_COMPOSE_AVAILABLE=true
                export DOCKER_COMPOSE_CMD="docker compose"
            else
                print_warning "Docker Compose not found"
                export DOCKER_COMPOSE_AVAILABLE=false
            fi
        else
            print_warning "Docker is installed but not running"
            print_info "Please start Docker Desktop or Docker daemon"
            export DOCKER_AVAILABLE=false
            export DOCKER_COMPOSE_AVAILABLE=false
        fi
    else
        print_info "Docker not found (optional for local development)"
        export DOCKER_AVAILABLE=false
        export DOCKER_COMPOSE_AVAILABLE=false
    fi
}

#######################################
# Virtual environment setup
#######################################
setup_virtual_environment() {
    print_header "Python Virtual Environment Setup"
    
    if [ -d "venv" ]; then
        print_step "Virtual environment already exists"
        if confirm_action "Recreate virtual environment?"; then
            print_substep "Removing existing virtual environment..."
            rm -rf venv
        else
            print_substep "Using existing virtual environment"
        fi
    fi
    
    if [ ! -d "venv" ]; then
        print_substep "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_step "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_substep "Activating virtual environment..."
    if [[ "$(get_os)" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Upgrade pip in virtual environment
    print_substep "Upgrading pip in virtual environment..."
    pip install --upgrade pip --quiet
    
    print_step "Virtual environment ready"
}

#######################################
# Dependency installation
#######################################
install_dependencies() {
    print_header "Dependency Installation"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_substep "Installing core dependencies..."
    pip install -r requirements.txt --quiet
    
    if [ "$DEV_MODE" = true ]; then
        print_substep "Installing development dependencies..."
        pip install pytest pytest-asyncio pytest-cov black flake8 mypy --quiet
    fi
    
    print_step "All dependencies installed successfully"
}

#######################################
# Environment configuration
#######################################
setup_environment_config() {
    print_header "Environment Configuration"
    
    if [ -f ".env" ]; then
        print_step ".env file already exists"
        if confirm_action "Overwrite existing .env file?"; then
            rm .env
        else
            print_substep "Keeping existing .env file"
            return
        fi
    fi
    
    if [ -f ".env.template" ]; then
        print_substep "Creating .env from template..."
        cp .env.template .env
        print_step ".env file created from template"
    else
        print_substep "Creating basic .env file..."
        create_basic_env_file
        print_step "Basic .env file created"
    fi
    
    print_warning "🔑 IMPORTANT: You must configure API keys in the .env file!"
    print_info "Required API keys:"
    print_info "  • OpenAI API key (for ChatGPT and embeddings)"
    print_info "  • Tavily API key (for web search)"
    print_info "  • Elasticsearch credentials (if using cloud)"
    echo
    
    if confirm_action "Open .env file for editing now?"; then
        open_env_file_for_editing
    fi
}

create_basic_env_file() {
    cat > .env << 'EOF'
# Data Protection AI Assistant Configuration
# Edit these values with your actual API keys and settings

# OpenAI Configuration
OPENAI_CHAT_API_KEY=your_openai_api_key_here
OPENAI_EMBED_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4
OPENAI_EMBED_MODEL=text-embedding-ada-002

# Azure OpenAI Configuration (alternative to OpenAI)
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_elasticsearch_password

# Tavily API (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# Application Settings
API_HOST=localhost
API_PORT=8000
UI_HOST=localhost
UI_PORT=7860
DEBUG=false
LOG_LEVEL=INFO

# Search Configuration
SEARCH_K=5
SEARCH_SCORE_THRESHOLD=0.5
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF
}

open_env_file_for_editing() {
    local os=$(get_os)
    case $os in
        "macos")
            if command_exists code; then
                code .env
            elif command_exists nano; then
                nano .env
            else
                open .env
            fi
            ;;
        "linux")
            if command_exists code; then
                code .env
            elif command_exists nano; then
                nano .env
            elif command_exists vim; then
                vim .env
            else
                print_info "Please edit .env manually with your preferred editor"
            fi
            ;;
        "windows")
            if command_exists code; then
                code .env
            else
                notepad .env
            fi
            ;;
    esac
}

#######################################
# Directory structure setup
#######################################
create_project_directories() {
    print_header "Project Directory Setup"
    
    local directories=(
        "logs"
        "data/gdpr"
        "data/uupdp"
        "data/company"
        "tests"
        "docs"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_substep "Created directory: $dir"
        else
            print_substep "Directory exists: $dir"
        fi
    done
    
    # Create sample documents if they don't exist
    create_sample_documents
    
    print_step "Project directories ready"
}

create_sample_documents() {
    # Create sample GDPR document if directory is empty
    if [ ! "$(ls -A data/gdpr 2>/dev/null)" ]; then
        cat > data/gdpr/sample_gdpr.txt << 'EOF'
# GDPR Key Principles Sample Document

## Article 5 - Principles relating to processing of personal data

1. Personal data shall be:
   a) processed lawfully, fairly and in a transparent manner
   b) collected for specified, explicit and legitimate purposes
   c) adequate, relevant and limited to what is necessary
   d) accurate and, where necessary, kept up to date
   e) kept in a form which permits identification for no longer than necessary
   f) processed in a manner that ensures appropriate security

## Article 6 - Lawfulness of processing

Processing shall be lawful only if and to the extent that at least one of the following applies:
- the data subject has given consent
- processing is necessary for the performance of a contract
- processing is necessary for compliance with a legal obligation
- processing is necessary in order to protect the vital interests
- processing is necessary for the performance of a task carried out in the public interest
- processing is necessary for the purposes of legitimate interests
EOF
        print_substep "Created sample GDPR document"
    fi
    
    # Create sample UU PDP document if directory is empty
    if [ ! "$(ls -A data/uupdp 2>/dev/null)" ]; then
        cat > data/uupdp/sample_uupdp.txt << 'EOF'
# UU PDP Sample Document - Key Provisions

## Article 20 - Principles of Personal Data Processing

Personal data processing must be based on:
1. Lawfulness and fairness
2. Purpose limitation
3. Data minimization
4. Accuracy
5. Storage limitation
6. Integrity and confidentiality
7. Accountability

## Article 21 - Legal Basis for Processing

Personal data processing is lawful if:
- Based on explicit consent
- Required for contract performance
- Required by law
- Necessary for vital interests
- Required for public interest
- Based on legitimate interests
EOF
        print_substep "Created sample UU PDP document"
    fi
}

#######################################
# Elasticsearch setup
#######################################
setup_elasticsearch() {
    print_header "Elasticsearch Setup"
    
    if [ "$SKIP_ES" = true ]; then
        print_info "Elasticsearch setup skipped by user request"
        return
    fi
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
        if confirm_action "Start Elasticsearch using Docker?"; then
            print_substep "Starting Elasticsearch container..."
            
            # Check if elasticsearch is already running
            if docker ps | grep -q elasticsearch; then
                print_step "Elasticsearch is already running"
            else
                # Start elasticsearch using docker-compose
                if [ -f "docker-compose.yml" ]; then
                    $DOCKER_COMPOSE_CMD up -d elasticsearch
                else
                    # Run standalone elasticsearch container
                    docker run -d \
                        --name elasticsearch \
                        -p 9200:9200 \
                        -e "discovery.type=single-node" \
                        -e "xpack.security.enabled=false" \
                        elasticsearch:8.11.0
                fi
                
                print_substep "Waiting for Elasticsearch to start..."
                local max_attempts=30
                local attempt=1
                
                while [ $attempt -le $max_attempts ]; do
                    if curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; then
                        print_step "Elasticsearch is running and healthy"
                        break
                    fi
                    
                    if [ $attempt -eq $max_attempts ]; then
                        print_warning "Elasticsearch may not be ready yet"
                        print_info "Check status with: docker logs elasticsearch"
                        break
                    fi
                    
                    print_substep "Waiting... (attempt $attempt/$max_attempts)"
                    sleep 2
                    ((attempt++))
                done
            fi
        fi
    else
        print_warning "Docker not available for Elasticsearch setup"
        print_info "Manual Elasticsearch installation required"
        print_info "Download from: https://www.elastic.co/downloads/elasticsearch"
        print_info "Or use cloud service: https://cloud.elastic.co/"
    fi
}

#######################################
# Installation testing
#######################################
test_installation() {
    print_header "Installation Testing"
    
    # Test Python imports
    print_substep "Testing Python module imports..."
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from src.core.config import Config
    print('✅ Core configuration module imported')
except ImportError as e:
    print(f'❌ Configuration import failed: {e}')
    sys.exit(1)

try:
    from src.services.search_engine import SearchEngine
    print('✅ Search engine module imported')
except ImportError as e:
    print(f'❌ Search engine import failed: {e}')
    sys.exit(1)

try:
    from src.agents.qa_engine import QAEngine
    print('✅ QA engine module imported')
except ImportError as e:
    print(f'❌ QA engine import failed: {e}')
    sys.exit(1)

print('✅ All core modules imported successfully')
" 2>/dev/null; then
        print_step "Python modules test passed"
    else
        print_warning "Some Python modules failed to import"
        print_info "This might be normal if API keys are not configured yet"
    fi
    
    # Test configuration
    if [ -f ".env" ]; then
        print_step "Configuration file exists"
    else
        print_warning "No .env file found"
    fi
    
    # Test Elasticsearch connectivity (if running)
    print_substep "Testing Elasticsearch connectivity..."
    if curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; then
        print_step "Elasticsearch is accessible"
    else
        print_info "Elasticsearch not accessible (may need to be started manually)"
    fi
}

#######################################
# Service management
#######################################
start_services() {
    if [ "$AUTO_START" = false ]; then
        return
    fi
    
    print_header "Starting Services"
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
        if confirm_action "Start all services with Docker?"; then
            print_substep "Starting all services..."
            $DOCKER_COMPOSE_CMD up -d
            
            print_substep "Waiting for services to be ready..."
            sleep 10
            
            # Check service health
            check_service_health
        fi
    else
        print_info "Docker not available. Services must be started manually."
        show_manual_start_instructions
    fi
}

check_service_health() {
    print_substep "Checking service health..."
    
    # Check API health
    local api_attempts=10
    local api_ready=false
    
    for i in $(seq 1 $api_attempts); do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_step "API service is healthy"
            api_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$api_ready" = false ]; then
        print_warning "API service not responding"
    fi
    
    # Check UI accessibility
    local ui_attempts=5
    local ui_ready=false
    
    for i in $(seq 1 $ui_attempts); do
        if curl -s http://localhost:7860 >/dev/null 2>&1; then
            print_step "UI service is accessible"
            ui_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$ui_ready" = false ]; then
        print_info "UI service may still be starting up"
    fi
}

show_manual_start_instructions() {
    print_info "Manual startup instructions:"
    echo
    print_color $YELLOW "1. Activate virtual environment:"
    if [[ "$(get_os)" == "windows" ]]; then
        echo "   venv\\Scripts\\activate"
    else
        echo "   source venv/bin/activate"
    fi
    echo
    print_color $YELLOW "2. Start Elasticsearch (if not already running):"
    echo "   docker run -d --name elasticsearch -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0"
    echo
    print_color $YELLOW "3. Start the application:"
    echo "   python main.py --both"
    echo
}

#######################################
# Final instructions and summary
#######################################
show_completion_summary() {
    print_header "🎉 Setup Complete!"
    
    print_success "Data Protection AI Assistant has been successfully set up!"
    echo
    
    print_color $CYAN "📋 Next Steps:"
    echo
    print_color $WHITE "1. 🔑 Configure API Keys"
    print_color $YELLOW "   Edit your .env file with the required API keys:"
    print_color $YELLOW "   • OpenAI API key for ChatGPT and embeddings"
    print_color $YELLOW "   • Tavily API key for web search functionality"
    echo
    
    print_color $WHITE "2. 📄 Add Legal Documents"
    print_color $YELLOW "   Place your legal documents in these folders:"
    print_color $YELLOW "   • data/gdpr/     - GDPR-related documents"
    print_color $YELLOW "   • data/uupdp/    - Indonesia UU PDP documents"
    print_color $YELLOW "   • data/company/  - Company policy documents"
    echo
    
    print_color $WHITE "3. 🚀 Start the Application"
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
        print_color $GREEN "   Option A: Docker (Recommended)"
        print_color $YELLOW "   $DOCKER_COMPOSE_CMD up -d"
        echo
    fi
    
    print_color $GREEN "   Option B: Local Development"
    if [[ "$(get_os)" == "windows" ]]; then
        print_color $YELLOW "   venv\\Scripts\\activate"
    else
        print_color $YELLOW "   source venv/bin/activate"
    fi
    print_color $YELLOW "   python main.py --both"
    echo
    
    print_color $WHITE "4. 🌐 Access the Application"
    print_color $YELLOW "   • Web Interface:      http://localhost:7860"
    print_color $YELLOW "   • API Documentation:  http://localhost:8000/docs"
    print_color $YELLOW "   • Health Check:       http://localhost:8000/health"
    echo
    
    print_color $CYAN "📚 Documentation:"
    print_color $YELLOW "   • README.md                    - Complete guide"
    print_color $YELLOW "   • docs/DOCUMENT_MANAGEMENT.md  - Document management"
    print_color $YELLOW "   • python main.py --help       - Command options"
    echo
    
    print_color $CYAN "🧪 Testing:"
    print_color $YELLOW "   • pytest tests/                    - Run test suite"
    print_color $YELLOW "   • python test_document_management.py  - Integration test"
    echo
    
    if [ "$DEV_MODE" = true ]; then
        print_color $CYAN "🛠️  Development Tools (Installed):"
        print_color $YELLOW "   • pytest       - Testing framework"
        print_color $YELLOW "   • black        - Code formatting"
        print_color $YELLOW "   • flake8       - Code linting"
        print_color $YELLOW "   • mypy         - Type checking"
        echo
    fi
    
    print_color $CYAN "❓ Need Help?"
    print_color $YELLOW "   • Check logs in the logs/ directory"
    print_color $YELLOW "   • Run ./setup.sh --help for options"
    print_color $YELLOW "   • Visit: https://github.com/adryanra97/data-protection-ai-assistant"
    echo
    
    print_success "Happy coding with Data Protection AI Assistant! 🚀"
}

#######################################
# Help and usage information
#######################################
show_help() {
    print_banner
    
    cat << EOF
$(print_color $WHITE "DESCRIPTION:")
    Comprehensive setup script for the Data Protection AI Assistant.
    Automates installation, configuration, and initial testing.

$(print_color $WHITE "USAGE:")
    $0 [OPTIONS]

$(print_color $WHITE "OPTIONS:")
    -h, --help          Show this help message and exit
    --skip-docker       Skip Docker-related setup and checks
    --skip-es           Skip Elasticsearch setup
    --dev               Development mode (install additional dev tools)
    --verbose           Enable verbose output
    --auto-start        Automatically start services after setup
    --version           Show script version

$(print_color $WHITE "SETUP MODES:")
    Normal Mode:        Interactive setup with user prompts
    Development Mode:   Includes testing and development tools
    Production Mode:    Optimized for deployment environments

$(print_color $WHITE "EXAMPLES:")
    $0                  # Interactive setup
    $0 --dev            # Development setup with extra tools
    $0 --skip-docker    # Setup without Docker
    $0 --auto-start     # Setup and start services automatically

$(print_color $WHITE "REQUIREMENTS:")
    • Python $PYTHON_MIN_VERSION+ (Python 3.11+ recommended)
    • At least ${REQUIRED_DISK_SPACE_MB}MB free disk space
    • Internet connection for downloading dependencies
    • Docker (optional, but recommended)

$(print_color $WHITE "WHAT THIS SCRIPT DOES:")
    1. ✅ Check system requirements and compatibility
    2. ✅ Set up Python virtual environment
    3. ✅ Install all required dependencies
    4. ✅ Create and configure environment files
    5. ✅ Set up project directory structure
    6. ✅ Configure Elasticsearch (optional)
    7. ✅ Test installation and imports
    8. ✅ Provide detailed usage instructions

$(print_color $WHITE "SUPPORT:")
    For issues or questions:
    • GitHub: https://github.com/adryanra97/data-protection-ai-assistant
    • Documentation: README.md and docs/ directory
    • Author: Adryan R A

EOF
}

#######################################
# Command line argument parsing
#######################################
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-es)
                SKIP_ES=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                set -x  # Enable bash debugging
                shift
                ;;
            --auto-start)
                AUTO_START=true
                shift
                ;;
            --version)
                echo "Data Protection AI Assistant Setup Script v$SCRIPT_VERSION"
                echo "Author: Adryan R A"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo
                show_help
                exit 1
                ;;
        esac
    done
}

#######################################
# Pre-flight checks
#######################################
preflight_checks() {
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "Please run this script from the project root directory"
        print_info "The directory should contain main.py and requirements.txt"
        exit 1
    fi
    
    # Check for existing installation
    if [ -d "venv" ] && [ -f ".env" ]; then
        print_warning "Existing installation detected"
        if ! confirm_action "Continue with setup (may overwrite existing configuration)?"; then
            print_info "Setup cancelled by user"
            exit 0
        fi
    fi
}

#######################################
# Main setup orchestration
#######################################
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Show banner
    print_banner
    
    # Pre-flight checks
    preflight_checks
    
    # System checks
    check_system_requirements
    check_python_version
    check_docker_availability
    
    # Main setup steps
    setup_virtual_environment
    install_dependencies
    setup_environment_config
    create_project_directories
    setup_elasticsearch
    test_installation
    start_services
    
    # Final summary
    show_completion_summary
    
    print_success "Setup completed successfully! 🎉"
    exit 0
}

#######################################
# Error handling
#######################################
trap 'print_error "Setup failed due to an error. Check the output above for details."; exit 1' ERR

# Run main function with all arguments
main "$@"
        if python -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)'; then
            print_status "Python $PYTHON_VERSION found"
            PYTHON_CMD="python"
        else
            print_error "Python 3.11+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.11+"
        exit 1
    fi
}

# Check if Docker is installed and running
check_docker() {
    print_info "Checking Docker..."
    
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            print_status "Docker is running"
        else
            print_warning "Docker is installed but not running"
            print_info "Please start Docker and run this script again"
            exit 1
        fi
    else
        print_warning "Docker not found"
        print_info "Docker is recommended for easy deployment"
        print_info "You can still run the application locally"
    fi
}

# Setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_status "Virtual environment ready"
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    pip install -r requirements.txt
    
    print_status "Dependencies installed"
}

# Setup environment file
setup_environment() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            cp .env.template .env
            print_status "Environment file created from template"
            print_warning "Please edit .env file with your API keys"
        else
            print_error ".env.template not found"
            exit 1
        fi
    else
        print_status "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data/gdpr
    mkdir -p data/uupdp  
    mkdir -p data/company
    
    print_status "Directories created"
}

# Run tests
run_tests() {
    print_info "Running tests..."
    
    if $PYTHON_CMD -m pytest --version &> /dev/null; then
        $PYTHON_CMD -m pytest tests/ -v
        print_status "Tests completed"
    else
        print_warning "pytest not available, skipping tests"
    fi
}

# Start services with Docker
start_docker() {
    print_info "Starting services with Docker..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
        print_status "Services started with Docker Compose"
        print_info "API will be available at: http://localhost:8000"
        print_info "Web UI will be available at: http://localhost:7860"
    else
        print_error "docker-compose not found"
        exit 1
    fi
}

# Start services locally
start_local() {
    print_info "Starting services locally..."
    
    print_warning "Make sure you have Elasticsearch running separately"
    print_info "Starting application..."
    
    $PYTHON_CMD main.py --both
}

# Main setup function
main() {
    echo
    print_info "Starting setup process..."
    
    check_python
    check_docker
    
    # Ask user for setup preference
    echo
    echo "Choose setup option:"
    echo "1) Docker setup (recommended)"
    echo "2) Local development setup"
    read -p "Enter your choice (1 or 2): " choice
    
    case $choice in
        1)
            print_info "Setting up with Docker..."
            setup_environment
            create_directories
            start_docker
            ;;
        2)
            print_info "Setting up for local development..."
            setup_venv
            install_dependencies
            setup_environment
            create_directories
            run_tests
            
            echo
            print_info "Setup completed!"
            print_warning "Before starting, please:"
            print_warning "1. Edit .env file with your API keys"
            print_warning "2. Start Elasticsearch (or use Docker: docker run -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0)"
            print_warning "3. Add your legal documents to data/ folders"
            echo
            print_info "To start the application, run:"
            echo "source venv/bin/activate"
            echo "python main.py --both"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo
    print_status "Setup completed successfully!"
    echo
    print_info "Next steps:"
    print_info "1. Configure your .env file with API keys"
    print_info "2. Add legal documents to the data/ folders"
    print_info "3. Access the application:"
    print_info "   - API Documentation: http://localhost:8000/docs"
    print_info "   - Web Interface: http://localhost:7860"
    print_info "   - Health Check: http://localhost:8000/health"
    echo
}

# Run main function
main "$@"
