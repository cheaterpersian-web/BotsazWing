#!/bin/bash

# اسکریپت نصب کاملاً خودکار پلتفرم تلگرام بات SaaS
# Fully Automated Telegram Bot SaaS Platform Installer

set -e

# رنگ‌ها
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# تابع لاگ
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[موفق]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[هشدار]${NC} $1"
}

log_error() {
    echo -e "${RED}[خطا]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[مرحله]${NC} $1"
}

# نمایش بنر
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           پلتفرم تلگرام بات SaaS - نصب خودکار              ║"
    echo "║                                                              ║"
    echo "║              Telegram Bot SaaS Platform                      ║"
    echo "║                   Auto Installer                            ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# بررسی ریشه بودن
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "این اسکریپت نباید با دسترسی root اجرا شود"
        log "لطفاً با کاربر عادی اجرا کنید"
        exit 1
    fi
}

# بررسی سیستم عامل
check_os() {
    log_step "بررسی سیستم عامل..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "سیستم عامل پشتیبانی نمی‌شود"
        exit 1
    fi
    
    log "سیستم عامل: $OS $VER"
    
    # بررسی پشتیبانی
    case $OS in
        *"Ubuntu"*|*"Debian"*|*"CentOS"*|*"Red Hat"*|*"Fedora"*)
            log_success "سیستم عامل پشتیبانی می‌شود"
            ;;
        *)
            log_warning "سیستم عامل ممکن است پشتیبانی نشود"
            ;;
    esac
}

# نصب پیش‌نیازها
install_prerequisites() {
    log_step "نصب پیش‌نیازها..."
    
    # به‌روزرسانی پکیج‌ها
    log "به‌روزرسانی پکیج‌ها..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -y
        sudo apt-get install -y curl wget git unzip
    elif command -v yum &> /dev/null; then
        sudo yum update -y
        sudo yum install -y curl wget git unzip
    elif command -v dnf &> /dev/null; then
        sudo dnf update -y
        sudo dnf install -y curl wget git unzip
    fi
    
    log_success "پیش‌نیازها نصب شد"
}

# نصب Docker
install_docker() {
    log_step "نصب Docker..."
    
    if command -v docker &> /dev/null; then
        log "Docker قبلاً نصب است"
        docker --version
    else
        log "نصب Docker..."
        
        # دانلود و اجرای اسکریپت نصب Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        
        # راه‌اندازی Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # اضافه کردن کاربر به گروه docker
        sudo usermod -aG docker $USER
        
        log_success "Docker نصب شد"
    fi
}

# نصب Docker Compose
install_docker_compose() {
    log_step "نصب Docker Compose..."
    
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        log "Docker Compose قبلاً نصب است"
        if command -v docker-compose &> /dev/null; then
            docker-compose --version
        else
            docker compose version
        fi
    else
        log "نصب Docker Compose..."
        
        # دریافت آخرین نسخه
        COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        
        # دانلود و نصب
        sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        
        # اعطای مجوز اجرا
        sudo chmod +x /usr/local/bin/docker-compose
        
        # ایجاد لینک نمادین
        sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        log_success "Docker Compose نصب شد"
    fi
}

# دریافت اطلاعات از کاربر
get_user_inputs() {
    log_step "دریافت اطلاعات مورد نیاز..."
    
    echo
    echo -e "${CYAN}لطفاً اطلاعات زیر را وارد کنید:${NC}"
    echo
    
    # توکن بات
    while true; do
        read -p "🤖 توکن بات تلگرام (از @BotFather): " BOT_TOKEN
        if [[ $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
            break
        else
            log_error "فرمت توکن صحیح نیست. مثال: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        fi
    done
    
    # شناسه ادمین
    while true; do
        read -p "👤 شناسه تلگرام شما (از @userinfobot): " ADMIN_ID
        if [[ "$ADMIN_ID" =~ ^[0-9]+$ ]]; then
            break
        else
            log_error "شناسه تلگرام باید عدد باشد"
        fi
    done
    
    # اطلاعات پرداخت
    read -p "🏦 شماره حساب بانکی: " BANK_ACCOUNT
    read -p "₿ آدرس کیف پول کریپتو: " CRYPTO_WALLET
    
    # تنظیمات دامنه
    read -p "🌐 دامنه (اختیاری، برای localhost خالی بگذارید): " DOMAIN
    if [ -z "$DOMAIN" ]; then
        DOMAIN="localhost"
        WEBHOOK_URL=""
    else
        WEBHOOK_URL="https://$DOMAIN"
    fi
    
    log_success "اطلاعات دریافت شد"
}

# تولید رمزهای عبور
generate_passwords() {
    log_step "تولید رمزهای عبور امن..."
    
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    MINIO_ACCESS_KEY=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    MINIO_SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    
    log_success "رمزهای عبور تولید شد"
}

# ایجاد فایل .env
create_env_file() {
    log_step "ایجاد فایل تنظیمات..."
    
    cat > .env << EOF
# تنظیمات پلتفرم تلگرام بات SaaS
# تولید شده در $(date)

# تنظیمات دیتابیس
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}

# کلیدهای امنیتی
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# تنظیمات تلگرام بات
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
TELEGRAM_WEBHOOK_URL=${WEBHOOK_URL}
API_TOKEN=${SECRET_KEY}

# تنظیمات ادمین
ADMIN_TELEGRAM_IDS=${ADMIN_ID}

# تنظیمات پرداخت
BANK_ACCOUNT_NUMBER=${BANK_ACCOUNT}
CRYPTO_WALLET_ADDRESS=${CRYPTO_WALLET}

# تنظیمات MinIO
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}

# تنظیمات مانیتورینگ
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
DEBUG=false

# تنظیمات پیشرفته
MAX_BOTS_PER_USER=10
DEPLOYMENT_TIMEOUT=300
EOF
    
    log_success "فایل .env ایجاد شد"
}

# ایجاد دایرکتوری‌ها
setup_directories() {
    log_step "ایجاد دایرکتوری‌های مورد نیاز..."
    
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p logs
    mkdir -p backups
    
    log_success "دایرکتوری‌ها ایجاد شد"
}

# ایجاد تنظیمات مانیتورینگ
create_monitoring_config() {
    log_step "ایجاد تنظیمات مانیتورینگ..."
    
    # تنظیمات Prometheus
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

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

    # تنظیمات Grafana
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

    log_success "تنظیمات مانیتورینگ ایجاد شد"
}

# تنظیم Nginx
setup_nginx() {
    log_step "تنظیم Nginx..."
    
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=bot:10m rate=5r/s;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    upstream bot {
        server bot:8080;
    }

    server {
        listen 80;
        server_name ${DOMAIN};

        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /webhook/ {
            limit_req zone=bot burst=10 nodelay;
            proxy_pass http://bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    log_success "تنظیمات Nginx ایجاد شد"
}

# ساخت و راه‌اندازی سرویس‌ها
start_services() {
    log_step "ساخت و راه‌اندازی سرویس‌ها..."
    
    # دریافت تصاویر پایه
    log "دریافت تصاویر پایه..."
    docker-compose pull postgres redis minio nginx prometheus grafana
    
    # ساخت تصاویر سفارشی
    log "ساخت تصاویر سفارشی..."
    docker-compose build
    
    # راه‌اندازی سرویس‌ها
    log "راه‌اندازی سرویس‌ها..."
    docker-compose up -d
    
    log_success "سرویس‌ها راه‌اندازی شد"
}

# انتظار برای آماده شدن سرویس‌ها
wait_for_services() {
    log_step "انتظار برای آماده شدن سرویس‌ها..."
    
    # انتظار برای دیتابیس
    log "انتظار برای دیتابیس..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U telegram_bot_user -d telegram_bot_saas; do sleep 2; done'
    
    # انتظار برای Redis
    log "انتظار برای Redis..."
    timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping; do sleep 2; done'
    
    # انتظار برای MinIO
    log "انتظار برای MinIO..."
    timeout 30 bash -c 'until curl -f http://localhost:9000/minio/health/live; do sleep 2; done'
    
    # انتظار برای بک‌اند
    log "انتظار برای بک‌اند..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    
    log_success "همه سرویس‌ها آماده است"
}

# تنظیم وب‌هوک تلگرام
setup_telegram_webhook() {
    if [ -n "$WEBHOOK_URL" ]; then
        log_step "تنظیم وب‌هوک تلگرام..."
        
        WEBHOOK_URL_FULL="${WEBHOOK_URL}/webhook/${BOT_TOKEN}"
        
        # تنظیم وب‌هوک
        curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
             -H "Content-Type: application/json" \
             -d "{\"url\": \"${WEBHOOK_URL_FULL}\"}" \
             -s -o /dev/null
        
        if [ $? -eq 0 ]; then
            log_success "وب‌هوک تلگرام تنظیم شد"
        else
            log_warning "خطا در تنظیم وب‌هوک تلگرام"
        fi
    fi
}

# ایجاد اسکریپت‌های مدیریت
create_management_scripts() {
    log_step "ایجاد اسکریپت‌های مدیریت..."
    
    # اسکریپت پشتیبان‌گیری
    cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker-compose exec -T postgres pg_dump -U telegram_bot_user telegram_bot_saas > $BACKUP_DIR/db_$DATE.sql
docker-compose exec -T minio mc mirror /data $BACKUP_DIR/files_$DATE/
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "files_*" -mtime +7 -exec rm -rf {} \;
echo "پشتیبان‌گیری کامل شد: $DATE"
EOF
    
    # اسکریپت به‌روزرسانی
    cat > update.sh << 'EOF'
#!/bin/bash
echo "شروع به‌روزرسانی..."
git pull origin main
docker-compose pull
docker-compose up -d
docker system prune -f
echo "به‌روزرسانی کامل شد!"
EOF
    
    # اسکریپت تست
    cat > test.sh << 'EOF'
#!/bin/bash
echo "تست سرویس‌ها..."
curl -f http://localhost:8000/health && echo "✅ بک‌اند" || echo "❌ بک‌اند"
curl -f http://localhost:3000 && echo "✅ فرانت‌اند" || echo "❌ فرانت‌اند"
curl -f http://localhost:8080/health && echo "✅ بات" || echo "❌ بات"
curl -f http://localhost:3001 && echo "✅ Grafana" || echo "❌ Grafana"
EOF
    
    chmod +x backup.sh update.sh test.sh
    
    log_success "اسکریپت‌های مدیریت ایجاد شد"
}

# تست نصب
test_installation() {
    log_step "تست نصب..."
    
    # تست سرویس‌ها
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "بک‌اند کار می‌کند"
    else
        log_error "بک‌اند کار نمی‌کند"
        return 1
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "فرانت‌اند کار می‌کند"
    else
        log_error "فرانت‌اند کار نمی‌کند"
        return 1
    fi
    
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_success "بات کار می‌کند"
    else
        log_error "بات کار نمی‌کند"
        return 1
    fi
    
    return 0
}

# نمایش خلاصه نصب
show_summary() {
    log_success "نصب با موفقیت کامل شد!"
    
    echo
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                    🎉 نصب کامل شد! 🎉                       ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo
    echo "🌐 دسترسی‌ها:"
    if [ "$DOMAIN" = "localhost" ]; then
        echo "  • بک‌اند API:     http://localhost:8000"
        echo "  • فرانت‌اند:        http://localhost:3000"
        echo "  • وب‌هوک بات:     http://localhost:8080"
        echo "  • کنسول MinIO:   http://localhost:9001"
        echo "  • Prometheus:    http://localhost:9090"
        echo "  • Grafana:       http://localhost:3001"
    else
        echo "  • بک‌اند API:     https://${DOMAIN}/api/"
        echo "  • فرانت‌اند:        https://${DOMAIN}/"
        echo "  • وب‌هوک بات:     https://${DOMAIN}/webhook/"
        echo "  • کنسول MinIO:   https://${DOMAIN}:9001"
        echo "  • Prometheus:    https://${DOMAIN}:9090"
        echo "  • Grafana:       https://${DOMAIN}:3001"
    fi
    echo
    echo "🔑 اطلاعات ورود:"
    echo "  • Grafana:         admin / ${GRAFANA_PASSWORD}"
    echo "  • MinIO:           ${MINIO_ACCESS_KEY} / ${MINIO_SECRET_KEY}"
    echo
    echo "📱 مراحل بعدی:"
    echo "  1. به داشبورد ادمین بروید"
    echo "  2. با شناسه تلگرام خود وارد شوید"
    echo "  3. تنظیمات پرداخت را بررسی کنید"
    echo "  4. اولین بات را تست کنید"
    echo
    echo "🛠️ مدیریت:"
    echo "  • تست سرویس‌ها:    ./test.sh"
    echo "  • پشتیبان‌گیری:    ./backup.sh"
    echo "  • به‌روزرسانی:     ./update.sh"
    echo "  • مشاهده لاگ‌ها:   docker-compose logs -f"
    echo
    echo "📚 مستندات:"
    echo "  • API Docs:        http://localhost:8000/docs"
    echo "  • Health Check:    http://localhost:8000/health"
    echo "  • راهنمای فارسی:   README-FA.md"
    echo
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                    موفق باشید! 🚀                          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
}

# تابع اصلی
main() {
    show_banner
    
    check_root
    check_os
    install_prerequisites
    install_docker
    install_docker_compose
    get_user_inputs
    generate_passwords
    create_env_file
    setup_directories
    create_monitoring_config
    setup_nginx
    start_services
    wait_for_services
    setup_telegram_webhook
    create_management_scripts
    
    if test_installation; then
        show_summary
    else
        log_error "خطا در نصب! لطفاً لاگ‌ها را بررسی کنید: docker-compose logs"
        exit 1
    fi
}

# اجرای تابع اصلی
main "$@"