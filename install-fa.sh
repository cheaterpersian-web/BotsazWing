#!/bin/bash

# اسکریپت نصب خودکار پلتفرم تلگرام بات SaaS
# Telegram Bot SaaS Platform Auto Installer

set -e

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # بدون رنگ

# توابع لاگ
log_info() {
    echo -e "${BLUE}[اطلاعات]${NC} $1"
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

# تابع برای دریافت ورودی از کاربر
get_input() {
    local prompt="$1"
    local default="$2"
    local required="$3"
    
    while true; do
        if [ -n "$default" ]; then
            read -p "$prompt [$default]: " input
            input=${input:-$default}
        else
            read -p "$prompt: " input
        fi
        
        if [ "$required" = "true" ] && [ -z "$input" ]; then
            log_error "این فیلد اجباری است!"
            continue
        fi
        
        echo "$input"
        break
    done
}

# تابع برای دریافت تایید
get_confirmation() {
    local prompt="$1"
    local default="$2"
    
    while true; do
        if [ -n "$default" ]; then
            read -p "$prompt [$default]: " input
            input=${input:-$default}
        else
            read -p "$prompt: " input
        fi
        
        case $input in
            [Yy]*|[بب]*|[آآ]*) return 0 ;;
            [Nn]*|[خخ]*) return 1 ;;
            *) log_error "لطفاً 'بله' یا 'خیر' وارد کنید" ;;
        esac
    done
}

# بررسی ریشه بودن
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "این اسکریپت نباید با دسترسی root اجرا شود"
        exit 1
    fi
}

# بررسی پیش‌نیازها
check_requirements() {
    log_step "بررسی پیش‌نیازهای سیستم..."
    
    # بررسی Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker نصب نیست. لطفاً ابتدا Docker را نصب کنید."
        log_info "دستور نصب Docker:"
        echo "curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "sudo sh get-docker.sh"
        echo "sudo usermod -aG docker \$USER"
        exit 1
    fi
    
    # بررسی Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose نصب نیست. لطفاً ابتدا Docker Compose را نصب کنید."
        exit 1
    fi
    
    # بررسی Git
    if ! command -v git &> /dev/null; then
        log_error "Git نصب نیست. لطفاً ابتدا Git را نصب کنید."
        exit 1
    fi
    
    # بررسی Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon در حال اجرا نیست. لطفاً Docker را راه‌اندازی کنید."
        exit 1
    fi
    
    log_success "همه پیش‌نیازها موجود است"
}

# دریافت اطلاعات از کاربر
get_user_inputs() {
    echo
    log_step "دریافت اطلاعات مورد نیاز..."
    echo
    
    # اطلاعات تلگرام بات
    echo -e "${CYAN}=== اطلاعات تلگرام بات ===${NC}"
    BOT_TOKEN=$(get_input "توکن بات تلگرام (از @BotFather دریافت کنید)" "" "true")
    
    # بررسی فرمت توکن
    if [[ ! $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        log_error "فرمت توکن بات صحیح نیست. مثال: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        exit 1
    fi
    
    # اطلاعات ادمین
    echo
    echo -e "${CYAN}=== اطلاعات ادمین ===${NC}"
    ADMIN_TELEGRAM_ID=$(get_input "شناسه تلگرام شما (از @userinfobot دریافت کنید)" "" "true")
    
    # بررسی عدد بودن شناسه
    if ! [[ "$ADMIN_TELEGRAM_ID" =~ ^[0-9]+$ ]]; then
        log_error "شناسه تلگرام باید عدد باشد"
        exit 1
    fi
    
    # اطلاعات پرداخت
    echo
    echo -e "${CYAN}=== اطلاعات پرداخت ===${NC}"
    BANK_ACCOUNT=$(get_input "شماره حساب بانکی" "1234567890" "true")
    CRYPTO_WALLET=$(get_input "آدرس کیف پول کریپتو" "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" "true")
    
    # تنظیمات دامنه
    echo
    echo -e "${CYAN}=== تنظیمات دامنه ===${NC}"
    if get_confirmation "آیا دامنه سفارشی دارید؟" "خیر"; then
        DOMAIN=$(get_input "دامنه شما (مثال: example.com)" "" "true")
        WEBHOOK_URL="https://$DOMAIN"
    else
        DOMAIN="localhost"
        WEBHOOK_URL=""
    fi
    
    # تنظیمات SSL
    if [ "$DOMAIN" != "localhost" ]; then
        echo
        if get_confirmation "آیا گواهی SSL دارید؟" "خیر"; then
            SSL_CERT_PATH=$(get_input "مسیر فایل گواهی SSL" "/path/to/cert.pem" "false")
            SSL_KEY_PATH=$(get_input "مسیر فایل کلید SSL" "/path/to/key.pem" "false")
        else
            SSL_CERT_PATH=""
            SSL_KEY_PATH=""
        fi
    else
        SSL_CERT_PATH=""
        SSL_KEY_PATH=""
    fi
    
    # تنظیمات پیشرفته
    echo
    echo -e "${CYAN}=== تنظیمات پیشرفته ===${NC}"
    if get_confirmation "آیا می‌خواهید تنظیمات پیشرفته را تغییر دهید؟" "خیر"; then
        MAX_BOTS_PER_USER=$(get_input "حداکثر تعداد بات برای هر کاربر" "10" "false")
        DEPLOYMENT_TIMEOUT=$(get_input "زمان انتظار برای استقرار (ثانیه)" "300" "false")
        SENTRY_DSN=$(get_input "Sentry DSN (اختیاری)" "" "false")
    else
        MAX_BOTS_PER_USER="10"
        DEPLOYMENT_TIMEOUT="300"
        SENTRY_DSN=""
    fi
    
    log_success "اطلاعات دریافت شد"
}

# تولید رمزهای عبور امن
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

# ایجاد فایل محیط
create_env_file() {
    log_step "ایجاد فایل تنظیمات..."
    
    if [[ -f .env ]]; then
        log_warning "فایل .env موجود است. پشتیبان‌گیری می‌شود..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
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
ADMIN_TELEGRAM_IDS=${ADMIN_TELEGRAM_ID}

# تنظیمات پرداخت
BANK_ACCOUNT_NUMBER=${BANK_ACCOUNT}
CRYPTO_WALLET_ADDRESS=${CRYPTO_WALLET}

# تنظیمات MinIO
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}

# تنظیمات مانیتورینگ
SENTRY_DSN=${SENTRY_DSN}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}

# تنظیمات پیشرفته
MAX_BOTS_PER_USER=${MAX_BOTS_PER_USER}
DEPLOYMENT_TIMEOUT=${DEPLOYMENT_TIMEOUT}

# تنظیمات SSL (اختیاری)
SSL_CERT_PATH=${SSL_CERT_PATH}
SSL_KEY_PATH=${SSL_KEY_PATH}
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
    
    if [ "$DOMAIN" != "localhost" ] && [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
        # تنظیمات SSL
        cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # تنظیمات SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # تنظیمات پایه
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 50M;

    # فشرده‌سازی
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # محدودیت نرخ
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=bot:10m rate=5r/s;

    # سرورهای upstream
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    upstream bot {
        server bot:8080;
    }

    # سرور اصلی
    server {
        listen 80;
        server_name ${DOMAIN};
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ${DOMAIN};

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # هدرهای امنیتی
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # مسیرهای API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # مسیرهای وب‌هوک بات
        location /webhook/ {
            limit_req zone=bot burst=10 nodelay;
            proxy_pass http://bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # داشبورد ادمین
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
    else
        # تنظیمات بدون SSL
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
    fi
    
    log_success "تنظیمات Nginx ایجاد شد"
}

# ساخت و راه‌اندازی سرویس‌ها
start_services() {
    log_step "ساخت و راه‌اندازی سرویس‌ها..."
    
    # دریافت تصاویر پایه
    log_info "دریافت تصاویر پایه..."
    docker-compose pull postgres redis minio nginx prometheus grafana
    
    # ساخت تصاویر سفارشی
    log_info "ساخت تصاویر سفارشی..."
    docker-compose build
    
    # راه‌اندازی سرویس‌ها
    log_info "راه‌اندازی سرویس‌ها..."
    docker-compose up -d
    
    log_success "سرویس‌ها راه‌اندازی شد"
}

# انتظار برای آماده شدن سرویس‌ها
wait_for_services() {
    log_step "انتظار برای آماده شدن سرویس‌ها..."
    
    # انتظار برای دیتابیس
    log_info "انتظار برای دیتابیس..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U telegram_bot_user -d telegram_bot_saas; do sleep 2; done'
    
    # انتظار برای Redis
    log_info "انتظار برای Redis..."
    timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping; do sleep 2; done'
    
    # انتظار برای MinIO
    log_info "انتظار برای MinIO..."
    timeout 30 bash -c 'until curl -f http://localhost:9000/minio/health/live; do sleep 2; done'
    
    # انتظار برای بک‌اند
    log_info "انتظار برای بک‌اند..."
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

# ایجاد اسکریپت پشتیبان‌گیری
create_backup_script() {
    log_step "ایجاد اسکریپت پشتیبان‌گیری..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# اسکریپت پشتیبان‌گیری خودکار

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# پشتیبان‌گیری دیتابیس
docker-compose exec -T postgres pg_dump -U telegram_bot_user telegram_bot_saas > $BACKUP_DIR/db_$DATE.sql

# پشتیبان‌گیری فایل‌ها
docker-compose exec -T minio mc mirror /data $BACKUP_DIR/files_$DATE/

# حذف پشتیبان‌های قدیمی (بیش از 7 روز)
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "files_*" -mtime +7 -exec rm -rf {} \;

echo "پشتیبان‌گیری کامل شد: $DATE"
EOF
    
    chmod +x backup.sh
    log_success "اسکریپت پشتیبان‌گیری ایجاد شد"
}

# ایجاد اسکریپت به‌روزرسانی
create_update_script() {
    log_step "ایجاد اسکریپت به‌روزرسانی..."
    
    cat > update.sh << 'EOF'
#!/bin/bash
# اسکریپت به‌روزرسانی خودکار

echo "شروع به‌روزرسانی..."

# دریافت آخرین تغییرات
git pull origin main

# دریافت تصاویر جدید
docker-compose pull

# راه‌اندازی مجدد سرویس‌ها
docker-compose up -d

# پاک‌سازی سیستم
docker system prune -f

echo "به‌روزرسانی کامل شد!"
EOF
    
    chmod +x update.sh
    log_success "اسکریپت به‌روزرسانی ایجاد شد"
}

# نمایش خلاصه نصب
show_summary() {
    log_success "نصب با موفقیت کامل شد!"
    
    echo
    echo "=========================================="
    echo "  پلتفرم تلگرام بات SaaS"
    echo "=========================================="
    echo
    echo "سرویس‌ها:"
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
    echo "اطلاعات ورود:"
    echo "  • Grafana:         admin / ${GRAFANA_PASSWORD}"
    echo "  • MinIO:           ${MINIO_ACCESS_KEY} / ${MINIO_SECRET_KEY}"
    echo
    echo "مراحل بعدی:"
    echo "  1. به داشبورد ادمین بروید"
    echo "  2. با شناسه تلگرام خود وارد شوید"
    echo "  3. تنظیمات پرداخت را بررسی کنید"
    echo "  4. اولین بات را تست کنید"
    echo
    echo "مستندات:"
    echo "  • API Docs:        http://localhost:8000/docs"
    echo "  • Health Check:    http://localhost:8000/health"
    echo
    echo "لاگ‌ها:"
    echo "  • مشاهده لاگ‌ها:   docker-compose logs -f [service]"
    echo "  • همه سرویس‌ها:    docker-compose logs -f"
    echo
    echo "مدیریت:"
    echo "  • توقف سرویس‌ها:   docker-compose down"
    echo "  • راه‌اندازی:      docker-compose up -d"
    echo "  • راه‌اندازی مجدد: docker-compose restart"
    echo
    echo "پشتیبان‌گیری:"
    echo "  • پشتیبان‌گیری:    ./backup.sh"
    echo "  • به‌روزرسانی:     ./update.sh"
    echo
    echo "=========================================="
}

# تابع اصلی نصب
main() {
    echo "نصب‌کننده خودکار پلتفرم تلگرام بات SaaS"
    echo "========================================"
    echo
    
    check_root
    check_requirements
    get_user_inputs
    generate_passwords
    create_env_file
    setup_directories
    create_monitoring_config
    setup_nginx
    start_services
    wait_for_services
    setup_telegram_webhook
    create_backup_script
    create_update_script
    show_summary
}

# اجرای تابع اصلی
main "$@"