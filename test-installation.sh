#!/bin/bash

# اسکریپت تست نصب پلتفرم تلگرام بات SaaS
# Test Script for Telegram Bot SaaS Platform Installation

set -e

# رنگ‌ها
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 تست نصب پلتفرم تلگرام بات SaaS${NC}"
echo "====================================="
echo

# تابع تست
test_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="$3"
    
    echo -n "تست $service_name... "
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق${NC}"
        return 1
    fi
}

# تابع تست دیتابیس
test_database() {
    echo -n "تست اتصال دیتابیس... "
    
    if docker-compose exec -T postgres pg_isready -U telegram_bot_user -d telegram_bot_saas > /dev/null 2>&1; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق${NC}"
        return 1
    fi
}

# تابع تست Redis
test_redis() {
    echo -n "تست اتصال Redis... "
    
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق${NC}"
        return 1
    fi
}

# تابع تست MinIO
test_minio() {
    echo -n "تست اتصال MinIO... "
    
    if curl -f -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق${NC}"
        return 1
    fi
}

# تابع تست API
test_api() {
    echo -n "تست API بک‌اند... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق (کد: $response)${NC}"
        return 1
    fi
}

# تابع تست فرانت‌اند
test_frontend() {
    echo -n "تست فرانت‌اند... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق (کد: $response)${NC}"
        return 1
    fi
}

# تابع تست بات
test_bot() {
    echo -n "تست سرویس بات... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق (کد: $response)${NC}"
        return 1
    fi
}

# تابع تست Grafana
test_grafana() {
    echo -n "تست Grafana... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق (کد: $response)${NC}"
        return 1
    fi
}

# تابع تست Prometheus
test_prometheus() {
    echo -n "تست Prometheus... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ موفق${NC}"
        return 0
    else
        echo -e "${RED}❌ ناموفق (کد: $response)${NC}"
        return 1
    fi
}

# تابع بررسی وضعیت کانتینرها
check_containers() {
    echo -e "${BLUE}بررسی وضعیت کانتینرها:${NC}"
    echo
    
    docker-compose ps
    echo
}

# تابع بررسی منابع سیستم
check_resources() {
    echo -e "${BLUE}بررسی منابع سیستم:${NC}"
    echo
    
    echo "💾 حافظه:"
    free -h
    echo
    
    echo "💿 دیسک:"
    df -h
    echo
    
    echo "🐳 Docker:"
    docker system df
    echo
}

# تابع بررسی لاگ‌های خطا
check_logs() {
    echo -e "${BLUE}بررسی لاگ‌های خطا:${NC}"
    echo
    
    echo "🔍 جستجوی خطاها در لاگ‌ها..."
    
    # بررسی لاگ‌های بک‌اند
    if docker-compose logs backend 2>&1 | grep -i error | head -5; then
        echo -e "${YELLOW}⚠️ خطاهایی در بک‌اند یافت شد${NC}"
    else
        echo -e "${GREEN}✅ لاگ‌های بک‌اند پاک است${NC}"
    fi
    
    # بررسی لاگ‌های بات
    if docker-compose logs bot 2>&1 | grep -i error | head -5; then
        echo -e "${YELLOW}⚠️ خطاهایی در بات یافت شد${NC}"
    else
        echo -e "${GREEN}✅ لاگ‌های بات پاک است${NC}"
    fi
    
    # بررسی لاگ‌های دیتابیس
    if docker-compose logs postgres 2>&1 | grep -i error | head -5; then
        echo -e "${YELLOW}⚠️ خطاهایی در دیتابیس یافت شد${NC}"
    else
        echo -e "${GREEN}✅ لاگ‌های دیتابیس پاک است${NC}"
    fi
    
    echo
}

# تابع تست عملکرد
performance_test() {
    echo -e "${BLUE}تست عملکرد:${NC}"
    echo
    
    echo "⏱️ تست زمان پاسخ API..."
    start_time=$(date +%s%N)
    curl -s http://localhost:8000/health > /dev/null
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))
    echo "زمان پاسخ API: ${response_time}ms"
    
    if [ $response_time -lt 1000 ]; then
        echo -e "${GREEN}✅ عملکرد خوب${NC}"
    elif [ $response_time -lt 3000 ]; then
        echo -e "${YELLOW}⚠️ عملکرد متوسط${NC}"
    else
        echo -e "${RED}❌ عملکرد ضعیف${NC}"
    fi
    
    echo
}

# تابع خلاصه نتایج
summary() {
    local total_tests=$1
    local passed_tests=$2
    
    echo "====================================="
    echo -e "${BLUE}خلاصه نتایج تست:${NC}"
    echo "تست‌های انجام شده: $total_tests"
    echo "تست‌های موفق: $passed_tests"
    echo "تست‌های ناموفق: $((total_tests - passed_tests))"
    
    if [ $passed_tests -eq $total_tests ]; then
        echo -e "${GREEN}🎉 همه تست‌ها موفق بود! سیستم آماده استفاده است.${NC}"
    elif [ $passed_tests -gt $((total_tests / 2)) ]; then
        echo -e "${YELLOW}⚠️ بیشتر تست‌ها موفق بود، اما برخی مشکلات وجود دارد.${NC}"
    else
        echo -e "${RED}❌ بسیاری از تست‌ها ناموفق بود. لطفاً مشکلات را بررسی کنید.${NC}"
    fi
    
    echo "====================================="
}

# تابع اصلی
main() {
    local total_tests=0
    local passed_tests=0
    
    # بررسی وضعیت کانتینرها
    check_containers
    
    # بررسی منابع سیستم
    check_resources
    
    # تست سرویس‌ها
    echo -e "${BLUE}تست سرویس‌ها:${NC}"
    echo
    
    # تست دیتابیس
    total_tests=$((total_tests + 1))
    if test_database; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست Redis
    total_tests=$((total_tests + 1))
    if test_redis; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست MinIO
    total_tests=$((total_tests + 1))
    if test_minio; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست API
    total_tests=$((total_tests + 1))
    if test_api; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست فرانت‌اند
    total_tests=$((total_tests + 1))
    if test_frontend; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست بات
    total_tests=$((total_tests + 1))
    if test_bot; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست Grafana
    total_tests=$((total_tests + 1))
    if test_grafana; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # تست Prometheus
    total_tests=$((total_tests + 1))
    if test_prometheus; then
        passed_tests=$((passed_tests + 1))
    fi
    
    echo
    
    # بررسی لاگ‌ها
    check_logs
    
    # تست عملکرد
    performance_test
    
    # خلاصه نتایج
    summary $total_tests $passed_tests
    
    # پیشنهادات
    if [ $passed_tests -lt $total_tests ]; then
        echo
        echo -e "${YELLOW}پیشنهادات برای رفع مشکلات:${NC}"
        echo "1. لاگ‌ها را بررسی کنید: docker-compose logs"
        echo "2. سرویس‌ها را راه‌اندازی مجدد کنید: docker-compose restart"
        echo "3. منابع سیستم را بررسی کنید"
        echo "4. تنظیمات فایروال را بررسی کنید"
    fi
}

# اجرای تست
main