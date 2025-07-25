#!/bin/bash

# Data Protection AI Assistant Setup Script
# Author: Adryan R A

set -e

echo "Data Protection AI Assistant Setup"
echo "Author: Adryan R A"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW} $1${NC}"
}

print_error() {
    echo -e "${RED} $1${NC}"
}

print_info() {
    echo -e "${BLUE} $1${NC}"
}

# Check if Python 3.11+ is installed
check_python() {
    print_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)'; then
            print_status "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.11+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
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
