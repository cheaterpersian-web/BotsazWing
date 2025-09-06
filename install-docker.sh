#!/bin/bash

# اسکریپت نصب Docker و Docker Compose
# Docker and Docker Compose Installation Script

set -e

# رنگ‌ها
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐳 نصب Docker و Docker Compose${NC}"
echo "================================"
echo

# تشخیص سیستم عامل
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
    elif [ -f /etc/debian_version ]; then
        OS=Debian
        VER=$(cat /etc/debian_version)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    echo -e "${BLUE}سیستم عامل تشخیص داده شد: $OS $VER${NC}"
}

# بررسی نصب بودن Docker
check_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker قبلاً نصب است${NC}"
        docker --version
        return 0
    else
        echo -e "${YELLOW}⚠️ Docker نصب نیست${NC}"
        return 1
    fi
}

# بررسی نصب بودن Docker Compose
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose قبلاً نصب است${NC}"
        if command -v docker-compose &> /dev/null; then
            docker-compose --version
        else
            docker compose version
        fi
        return 0
    else
        echo -e "${YELLOW}⚠️ Docker Compose نصب نیست${NC}"
        return 1
    fi
}

# نصب Docker در Ubuntu/Debian
install_docker_ubuntu() {
    echo -e "${BLUE}نصب Docker در Ubuntu/Debian...${NC}"
    
    # به‌روزرسانی پکیج‌ها
    sudo apt-get update
    
    # نصب پیش‌نیازها
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # اضافه کردن کلید GPG رسمی Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # اضافه کردن مخزن Docker
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # به‌روزرسانی پکیج‌ها
    sudo apt-get update
    
    # نصب Docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker نصب شد${NC}"
}

# نصب Docker در CentOS/RHEL
install_docker_centos() {
    echo -e "${BLUE}نصب Docker در CentOS/RHEL...${NC}"
    
    # حذف نسخه‌های قدیمی
    sudo yum remove -y docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-engine
    
    # نصب پیش‌نیازها
    sudo yum install -y yum-utils
    
    # اضافه کردن مخزن Docker
    sudo yum-config-manager \
        --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
    
    # نصب Docker
    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker نصب شد${NC}"
}

# نصب Docker در Fedora
install_docker_fedora() {
    echo -e "${BLUE}نصب Docker در Fedora...${NC}"
    
    # حذف نسخه‌های قدیمی
    sudo dnf remove -y docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-selinux \
        docker-engine-selinux \
        docker-engine
    
    # نصب پیش‌نیازها
    sudo dnf install -y dnf-plugins-core
    
    # اضافه کردن مخزن Docker
    sudo dnf config-manager \
        --add-repo \
        https://download.docker.com/linux/fedora/docker-ce.repo
    
    # نصب Docker
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker نصب شد${NC}"
}

# نصب Docker Compose جداگانه
install_docker_compose_standalone() {
    echo -e "${BLUE}نصب Docker Compose جداگانه...${NC}"
    
    # دریافت آخرین نسخه
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # دانلود و نصب
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # اعطای مجوز اجرا
    sudo chmod +x /usr/local/bin/docker-compose
    
    # ایجاد لینک نمادین
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker Compose نصب شد${NC}"
}

# راه‌اندازی Docker
setup_docker() {
    echo -e "${BLUE}راه‌اندازی Docker...${NC}"
    
    # شروع سرویس Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # اضافه کردن کاربر به گروه docker
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker راه‌اندازی شد${NC}"
}

# تست نصب
test_installation() {
    echo -e "${BLUE}تست نصب...${NC}"
    
    # تست Docker
    if sudo docker run hello-world > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker کار می‌کند${NC}"
    else
        echo -e "${RED}❌ Docker کار نمی‌کند${NC}"
        return 1
    fi
    
    # تست Docker Compose
    if docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker Compose کار می‌کند${NC}"
    else
        echo -e "${RED}❌ Docker Compose کار نمی‌کند${NC}"
        return 1
    fi
    
    return 0
}

# نمایش اطلاعات نصب
show_info() {
    echo
    echo "=========================================="
    echo -e "${GREEN}🎉 نصب Docker و Docker Compose کامل شد!${NC}"
    echo "=========================================="
    echo
    
    echo -e "${BLUE}اطلاعات نصب:${NC}"
    docker --version
    if command -v docker-compose &> /dev/null; then
        docker-compose --version
    else
        docker compose version
    fi
    
    echo
    echo -e "${YELLOW}⚠️ نکات مهم:${NC}"
    echo "1. برای استفاده از Docker بدون sudo، از سیستم خارج شوید و دوباره وارد شوید"
    echo "2. یا دستور زیر را اجرا کنید: newgrp docker"
    echo "3. برای تست، دستور زیر را اجرا کنید: docker run hello-world"
    echo
    
    echo -e "${BLUE}مراحل بعدی:${NC}"
    echo "1. از سیستم خارج شوید و دوباره وارد شوید"
    echo "2. اسکریپت نصب پلتفرم را اجرا کنید: ./quick-install.sh"
    echo
    echo "=========================================="
}

# تابع اصلی
main() {
    # تشخیص سیستم عامل
    detect_os
    
    # بررسی نصب بودن Docker
    if check_docker; then
        DOCKER_INSTALLED=true
    else
        DOCKER_INSTALLED=false
    fi
    
    # بررسی نصب بودن Docker Compose
    if check_docker_compose; then
        COMPOSE_INSTALLED=true
    else
        COMPOSE_INSTALLED=false
    fi
    
    # اگر هر دو نصب هستند
    if [ "$DOCKER_INSTALLED" = true ] && [ "$COMPOSE_INSTALLED" = true ]; then
        echo -e "${GREEN}✅ Docker و Docker Compose قبلاً نصب هستند!${NC}"
        show_info
        exit 0
    fi
    
    # نصب Docker
    if [ "$DOCKER_INSTALLED" = false ]; then
        case $OS in
            *"Ubuntu"*|*"Debian"*)
                install_docker_ubuntu
                ;;
            *"CentOS"*|*"Red Hat"*)
                install_docker_centos
                ;;
            *"Fedora"*)
                install_docker_fedora
                ;;
            *)
                echo -e "${YELLOW}سیستم عامل پشتیبانی نمی‌شود. لطفاً Docker را دستی نصب کنید.${NC}"
                echo "راهنمای نصب: https://docs.docker.com/get-docker/"
                exit 1
                ;;
        esac
        
        # راه‌اندازی Docker
        setup_docker
    fi
    
    # نصب Docker Compose
    if [ "$COMPOSE_INSTALLED" = false ]; then
        # بررسی اینکه آیا Docker Compose plugin نصب شده یا نه
        if ! docker compose version &> /dev/null; then
            install_docker_compose_standalone
        fi
    fi
    
    # تست نصب
    if test_installation; then
        show_info
    else
        echo -e "${RED}❌ خطا در نصب! لطفاً مشکلات را بررسی کنید.${NC}"
        exit 1
    fi
}

# اجرای تابع اصلی
main "$@"