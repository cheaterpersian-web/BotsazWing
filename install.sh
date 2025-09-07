#!/bin/bash

# Telegram Bot SaaS Platform Installation Script
# This script sets up the entire platform with one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Proceeding in root mode."
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        log_info "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        log_info "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

# Generate random passwords
generate_passwords() {
    log_info "Generating secure passwords..."
    
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    MINIO_ACCESS_KEY=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    MINIO_SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    
    log_success "Passwords generated"
}

# Create environment file
create_env_file() {
    log_info "Creating environment configuration..."
    
    if [[ -f .env ]]; then
        log_warning ".env file already exists. Creating backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    cat > .env << EOF
# Telegram Bot SaaS Platform Environment Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}

# Security Keys
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_WEBHOOK_URL=
API_TOKEN=${SECRET_KEY}

# Admin Configuration
ADMIN_TELEGRAM_IDS=

# Payment Configuration
BANK_ACCOUNT_NUMBER=1234567890
CRYPTO_WALLET_ADDRESS=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# MinIO Configuration
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}

# Monitoring Configuration
SENTRY_DSN=
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
EOF
    
    # Add host port mappings to avoid conflicts
    cat >> .env << EOF

# Host port mappings
HOST_POSTGRES_PORT=15432
HOST_REDIS_PORT=16379
HOST_BACKEND_PORT=18000
HOST_FRONTEND_PORT=3000
EOF

    log_success "Environment file created"
}

# Setup directories
setup_directories() {
    log_info "Setting up directories..."
    
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p logs
    
    log_success "Directories created"
}

# Create monitoring configuration
create_monitoring_config() {
    log_info "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'bot'
    static_configs:
      - targets: ['bot:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF

    # Grafana datasource configuration
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    log_success "Monitoring configuration created"
}

# Build and start services
start_services() {
    log_info "Building and starting services..."
    
    # Pull base images
    log_info "Pulling base images..."
    docker-compose pull postgres redis minio nginx prometheus grafana
    
    # Build custom images
    log_info "Building custom images..."
    docker-compose build
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    log_success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for database..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U telegram_bot_user -d telegram_bot_saas; do sleep 2; done'
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for MinIO
    log_info "Waiting for MinIO..."
    timeout 30 bash -c 'until curl -f http://localhost:9000/minio/health/live; do sleep 2; done'
    
    # Wait for backend
    log_info "Waiting for backend..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    
    log_success "All services are ready"
}

# Display installation summary
show_summary() {
    log_success "Installation completed successfully!"
    
    echo
    echo "=========================================="
    echo "  Telegram Bot SaaS Platform"
    echo "=========================================="
    echo
    echo "Services:"
    echo "  • Backend API:     http://localhost:8000"
    echo "  • Frontend:        http://localhost:3000"
    echo "  • Bot Webhook:     http://localhost:8080"
    echo "  • MinIO Console:   http://localhost:9001"
    echo "  • Prometheus:      http://localhost:9090"
    echo "  • Grafana:         http://localhost:3001"
    echo
    echo "Credentials:"
    echo "  • Grafana:         admin / ${GRAFANA_PASSWORD}"
    echo "  • MinIO:           ${MINIO_ACCESS_KEY} / ${MINIO_SECRET_KEY}"
    echo
    echo "Next Steps:"
    echo "  1. Update .env file with your Telegram bot token"
    echo "  2. Set ADMIN_TELEGRAM_IDS in .env file"
    echo "  3. Configure payment details (bank account, crypto wallet)"
    echo "  4. Restart services: docker-compose restart"
    echo
    echo "Documentation:"
    echo "  • API Docs:        http://localhost:8000/docs"
    echo "  • Health Check:    http://localhost:8000/health"
    echo
    echo "Logs:"
    echo "  • View logs:       docker-compose logs -f [service]"
    echo "  • All services:    docker-compose logs -f"
    echo
    echo "Management:"
    echo "  • Stop services:   docker-compose down"
    echo "  • Start services:  docker-compose up -d"
    echo "  • Restart:         docker-compose restart"
    echo
    echo "=========================================="
}

# Main installation function
main() {
    echo "Telegram Bot SaaS Platform Installer"
    echo "===================================="
    echo
    
    check_root
    check_requirements
    generate_passwords
    create_env_file
    setup_directories
    create_monitoring_config
    start_services
    wait_for_services
    show_summary
}

# Run main function
main "$@"