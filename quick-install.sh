#!/bin/bash

# اسکریپت نصب سریع پلتفرم تلگرام بات SaaS
# Quick Install Script for Telegram Bot SaaS Platform

set -e

# رنگ‌ها
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 نصب سریع پلتفرم تلگرام بات SaaS${NC}"
echo "=================================="
echo

# بررسی پیش‌نیازها
echo -e "${YELLOW}بررسی پیش‌نیازها...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker نصب نیست!${NC}"
    echo "لطفاً ابتدا Docker را نصب کنید:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose نصب نیست!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ پیش‌نیازها موجود است${NC}"
echo

# Detect compose command (v2 preferred)
if docker compose version > /dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose > /dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  echo -e "${RED}❌ Docker Compose نصب نیست!${NC}"
  exit 1
fi

# دریافت اطلاعات ضروری
echo -e "${BLUE}لطفاً اطلاعات زیر را وارد کنید:${NC}"
echo

read -p "🤖 توکن بات تلگرام (از @BotFather): " BOT_TOKEN
if [[ ! $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
    echo -e "${RED}❌ فرمت توکن صحیح نیست!${NC}"
    exit 1
fi

read -p "👤 شناسه تلگرام شما (از @userinfobot): " ADMIN_ID
if ! [[ "$ADMIN_ID" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ شناسه تلگرام باید عدد باشد!${NC}"
    exit 1
fi

read -p "🏦 شماره حساب بانکی: " BANK_ACCOUNT
read -p "₿ آدرس کیف پول کریپتو: " CRYPTO_WALLET

echo
echo -e "${YELLOW}در حال نصب...${NC}"

# تولید رمزهای عبور
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
MINIO_ACCESS_KEY=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
MINIO_SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)

# ایجاد فایل .env
cat > .env << EOF
# تنظیمات پلتفرم تلگرام بات SaaS
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${POSTGRES_PASSWORD}
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
TELEGRAM_WEBHOOK_URL=
API_TOKEN=${SECRET_KEY}
ADMIN_TELEGRAM_IDS=${ADMIN_ID}
BANK_ACCOUNT_NUMBER=${BANK_ACCOUNT}
CRYPTO_WALLET_ADDRESS=${CRYPTO_WALLET}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
DEBUG=false

# پورت‌های هاست (برای جلوگیری از تداخل)
HOST_POSTGRES_PORT=15432
HOST_REDIS_PORT=16379
HOST_BACKEND_PORT=18000
HOST_FRONTEND_PORT=3000
HOST_NGINX_HTTP_PORT=18080
HOST_NGINX_HTTPS_PORT=18443
EOF

# ایجاد دایرکتوری‌ها
mkdir -p nginx/ssl monitoring/grafana/{dashboards,datasources} logs

# تنظیمات مانیتورینگ
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  - job_name: 'bot'
    static_configs:
      - targets: ['bot:8080']
EOF

cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# راه‌اندازی سرویس‌ها
echo -e "${YELLOW}در حال راه‌اندازی سرویس‌ها...${NC}"
$COMPOSE pull postgres redis minio nginx prometheus grafana
$COMPOSE build
$COMPOSE up -d

# انتظار برای آماده شدن
echo -e "${YELLOW}انتظار برای آماده شدن سرویس‌ها...${NC}"
sleep 30

# بررسی وضعیت
if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ نصب با موفقیت کامل شد!${NC}"
    echo
    echo "=========================================="
    echo "  🎉 پلتفرم آماده استفاده است!"
    echo "=========================================="
    echo
    echo "🌐 دسترسی‌ها:"
    echo "  • داشبورد ادمین: http://localhost:3000"
    echo "  • API Docs:      http://localhost:8000/docs"
    echo "  • مانیتورینگ:    http://localhost:3001"
    echo
    echo "🔑 اطلاعات ورود:"
    echo "  • Grafana: admin / ${GRAFANA_PASSWORD}"
    echo "  • MinIO:   ${MINIO_ACCESS_KEY} / ${MINIO_SECRET_KEY}"
    echo
    echo "📱 مراحل بعدی:"
    echo "  1. به http://localhost:3000 بروید"
    echo "  2. با شناسه ${ADMIN_ID} وارد شوید"
    echo "  3. بات خود را در تلگرام پیدا کنید"
    echo "  4. /start را ارسال کنید"
    echo
    echo "=========================================="
else
    echo -e "${RED}❌ خطا در نصب!${NC}"
    echo "لاگ‌ها را بررسی کنید: $COMPOSE logs"
    exit 1
fi