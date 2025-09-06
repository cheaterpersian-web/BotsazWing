# پلتفرم تلگرام بات SaaS

یک پلتفرم حرفه‌ای SaaS برای استقرار و مدیریت بات‌های تلگرام از مخازن GitHub با سیستم اشتراک.

## 🚀 ویژگی‌ها

- **استقرار چندمستاجری بات‌ها**: استقرار بات‌ها از مخازن GitHub با کانتینرهای Docker
- **مدیریت اشتراک**: پلان‌های ماهانه، دو ماهه و سفارشی
- **پردازش پرداخت**: پشتیبانی از انتقال بانکی و پرداخت کریپتو با تایید دستی
- **داشبورد ادمین**: پنل مدیریت وب برای مدیریت کاربران، بات‌ها و اشتراک‌ها
- **مدیریت خودکار**: کارهای cron برای بررسی اشتراک‌ها و مدیریت چرخه عمر کانتینر
- **امنیت**: ذخیره رمزگذاری شده توکن‌ها و اقدامات امنیتی جامع
- **مانیتورینگ**: مانیتورینگ داخلی با Prometheus و Grafana
- **مقیاس‌پذیری**: معماری مبتنی بر Docker برای مقیاس‌پذیری آسان

## 🏗️ معماری

### سرویس‌های بک‌اند
- **بک‌اند FastAPI**: REST API با دیتابیس PostgreSQL
- **بات تلگرام**: بات مبتنی بر aiogram برای تعامل کاربر
- **کارگران Celery**: پردازش کارهای پس‌زمینه
- **Redis**: کش و ذخیره جلسات
- **MinIO**: ذخیره فایل برای رسیدها و لاگ‌ها

### فرانت‌اند
- **داشبورد ادمین React**: رابط وب مدرن با TailwindCSS
- **احراز هویت JWT**: دسترسی امن ادمین
- **به‌روزرسانی‌های بلادرنگ**: مانیتورینگ وضعیت زنده

### زیرساخت
- **Docker Compose**: ارکستراسیون چند سرویس
- **Nginx**: پروکسی معکوس و متعادل‌ساز بار
- **PostgreSQL**: دیتابیس اصلی
- **Prometheus + Grafana**: مانیتورینگ و هشدار

## 📋 پیش‌نیازها

- Docker و Docker Compose
- Git
- 4GB+ RAM
- 20GB+ فضای دیسک
- Linux/macOS/Windows با WSL2

## 🛠️ نصب

### نصب سریع (توصیه می‌شود)

```bash
./quick-install.sh
```

### نصب کامل با تنظیمات پیشرفته

```bash
./install-fa.sh
```

### نصب دستی

1. **کلون کردن مخزن**
   ```bash
   git clone <repository-url>
   cd telegram-bot-saas
   ```

2. **اجرای اسکریپت نصب**
   ```bash
   ./install-fa.sh
   ```

3. **پیکربندی توکن بات**
   ```bash
   # ویرایش فایل .env
   nano .env
   
   # به‌روزرسانی TELEGRAM_BOT_TOKEN با توکن بات از @BotFather
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

4. **راه‌اندازی مجدد سرویس‌ها**
   ```bash
   docker-compose restart
   ```

## 🔧 پیکربندی

### متغیرهای محیطی

| متغیر | توضیحات | پیش‌فرض |
|-------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | توکن بات از @BotFather | الزامی |
| `POSTGRES_PASSWORD` | رمز عبور دیتابیس | تولید خودکار |
| `SECRET_KEY` | کلید مخفی JWT | تولید خودکار |
| `ENCRYPTION_KEY` | کلید رمزگذاری توکن | تولید خودکار |
| `ADMIN_TELEGRAM_IDS` | شناسه‌های ادمین جدا شده با کاما | الزامی |
| `BANK_ACCOUNT_NUMBER` | شماره حساب بانکی برای پرداخت‌ها | الزامی |
| `CRYPTO_WALLET_ADDRESS` | آدرس کیف پول کریپتو برای پرداخت‌ها | الزامی |

### تنظیم ادمین

1. **دریافت شناسه تلگرام**
   - به @userinfobot در تلگرام پیام دهید
   - شناسه عددی خود را کپی کنید

2. **اضافه کردن شناسه ادمین به .env**
   ```bash
   ADMIN_TELEGRAM_IDS=123456789,987654321
   ```

3. **راه‌اندازی مجدد سرویس‌ها**
   ```bash
   docker-compose restart
   ```

## 📱 استفاده

### برای کاربران

1. **شروع بات**
   - بات خود را در تلگرام پیدا کنید
   - دستور `/start` را ارسال کنید

2. **ایجاد بات**
   - فرآیند راهنمایی شده راه‌اندازی را دنبال کنید
   - توکن بات خود را از @BotFather ارائه دهید
   - URL مخزن GitHub را وارد کنید
   - پلان اشتراک را انتخاب کنید
   - پرداخت را تکمیل کنید

3. **مدیریت بات‌های خود**
   - از `/mybots` برای مشاهده بات‌های مستقر شده استفاده کنید
   - وضعیت و لاگ‌ها را بررسی کنید
   - اشتراک‌ها را تمدید کنید

### برای ادمین‌ها

1. **دسترسی به داشبورد ادمین**
   - به `http://localhost:3000` بروید
   - با اطلاعات تلگرام خود وارد شوید

2. **مدیریت پلتفرم**
   - آمار کاربران را مشاهده کنید
   - پرداخت‌ها را تایید/رد کنید
   - استقرار بات‌ها را مانیتور کنید
   - اشتراک‌ها را مدیریت کنید

## 🔌 مستندات API

### احراز هویت

همه نقاط پایانی API نیاز به احراز هویت JWT دارند:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/
```

### نقاط پایانی کلیدی

- `GET /api/v1/users/` - لیست کاربران
- `GET /api/v1/bots/` - لیست نمونه‌های بات
- `POST /api/v1/bots/` - ایجاد نمونه بات
- `GET /api/v1/subscriptions/` - لیست اشتراک‌ها
- `GET /api/v1/payments/` - لیست پرداخت‌ها
- `POST /api/v1/payments/{id}/confirm` - تایید پرداخت

مستندات کامل API در دسترس است: `http://localhost:8000/docs`

## 🐳 سرویس‌های Docker

| سرویس | پورت | توضیحات |
|-------|------|---------|
| بک‌اند API | 8000 | برنامه FastAPI |
| فرانت‌اند | 3000 | داشبورد ادمین React |
| وب‌هوک بات | 8080 | وب‌هوک بات تلگرام |
| PostgreSQL | 5432 | دیتابیس |
| Redis | 6379 | کش و جلسات |
| MinIO | 9000/9001 | ذخیره فایل |
| Prometheus | 9090 | جمع‌آوری متریک‌ها |
| Grafana | 3001 | داشبورد مانیتورینگ |
| Nginx | 80/443 | پروکسی معکوس |

## 📊 مانیتورینگ

### داشبورد Grafana
- URL: `http://localhost:3001`
- نام کاربری: `admin`
- رمز عبور: در فایل `.env` بررسی کنید

### متریک‌های Prometheus
- URL: `http://localhost:9090`
- نقاط پایانی: `/metrics` روی همه سرویس‌ها

### بررسی سلامت
- بک‌اند: `http://localhost:8000/health`
- بات: `http://localhost:8080/health`
- فرانت‌اند: `http://localhost:3000`

## 🔒 امنیت

### محافظت از داده‌ها
- همه توکن‌های حساس در حالت استراحت رمزگذاری می‌شوند
- توکن‌های JWT برای احراز هویت API
- محدودیت نرخ روی همه نقاط پایانی
- اعتبارسنجی و پاک‌سازی ورودی

### امنیت شبکه
- جداسازی شبکه داخلی Docker
- پروکسی معکوس Nginx با هدرهای امنیتی
- پشتیبانی از HTTPS (گواهی‌های SSL را پیکربندی کنید)

### کنترل دسترسی
- دسترسی فقط ادمین به ویژگی‌های مدیریت
- جداسازی کاربر برای استقرار بات‌ها
- مدیریت امن آپلود فایل

## 🚀 استقرار

### استقرار تولید

1. **پیکربندی SSL**
   ```bash
   # اضافه کردن گواهی‌های SSL به nginx/ssl/
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

2. **به‌روزرسانی محیط**
   ```bash
   # تنظیم مقادیر تولید در .env
   DEBUG=false
   TELEGRAM_WEBHOOK_URL=https://yourdomain.com
   ```

3. **استقرار**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### مقیاس‌پذیری

- **مقیاس‌پذیری افقی**: اضافه کردن نمونه‌های بیشتر بک‌اند/بات
- **مقیاس‌پذیری دیتابیس**: استفاده از خوشه‌بندی PostgreSQL
- **ذخیره فایل**: استفاده از ذخیره سازگار با S3 خارجی
- **متعادل‌سازی بار**: پیکربندی سرورهای upstream Nginx

## 🛠️ توسعه

### توسعه محلی

1. **شروع سرویس‌های توسعه**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **اجرای تست‌ها**
   ```bash
   # تست‌های بک‌اند
   docker-compose exec backend pytest
   
   # تست‌های فرانت‌اند
   docker-compose exec frontend npm test
   ```

3. **فرمت‌بندی کد**
   ```bash
   # بک‌اند
   docker-compose exec backend black .
   docker-compose exec backend isort .
   
   # فرانت‌اند
   docker-compose exec frontend npm run format
   ```

### اضافه کردن ویژگی‌ها

1. **API بک‌اند**
   - اضافه کردن مسیرها در `backend/app/api/`
   - به‌روزرسانی اسکیماها در `backend/app/schemas.py`
   - اضافه کردن عملیات CRUD در `backend/app/crud.py`

2. **فرانت‌اند**
   - اضافه کردن صفحات در `frontend/src/pages/`
   - به‌روزرسانی کلاینت API در `frontend/src/services/api.ts`
   - اضافه کردن کامپوننت‌ها در `frontend/src/components/`

3. **بات**
   - اضافه کردن هندلرها در `bot/handlers/`
   - به‌روزرسانی میدل‌ویر در `bot/middleware/`
   - اضافه کردن ابزارها در `bot/utils/`

## 📝 نمونه‌های API

### ایجاد نمونه بات

```bash
curl -X POST "http://localhost:8000/api/v1/bots/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_name": "My Bot",
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "github_repo": "https://github.com/user/my-bot",
    "admin_numeric_id": 123456789
  }'
```

### تایید پرداخت

```bash
curl -X POST "http://localhost:8000/api/v1/payments/123e4567-e89b-12d3-a456-426614174000/confirm" \
  -H "Authorization: Bearer <admin-token>"
```

## 🐛 عیب‌یابی

### مشکلات رایج

1. **بات پاسخ نمی‌دهد**
   - توکن بات در `.env` را بررسی کنید
   - پیکربندی URL وب‌هوک را تأیید کنید
   - لاگ‌های کانتینر بات را بررسی کنید: `docker-compose logs bot`

2. **خطاهای اتصال دیتابیس**
   - اطمینان حاصل کنید که PostgreSQL در حال اجرا است: `docker-compose ps postgres`
   - اعتبارنامه‌های دیتابیس در `.env` را بررسی کنید
   - اتصال شبکه را تأیید کنید

3. **مشکلات تایید پرداخت**
   - سرویس MinIO را بررسی کنید: `docker-compose logs minio`
   - مجوزهای آپلود فایل را تأیید کنید
   - وضعیت پرداخت در داشبورد ادمین را بررسی کنید

4. **فرانت‌اند لود نمی‌شود**
   - ساخت React را بررسی کنید: `docker-compose logs frontend`
   - اتصال API را تأیید کنید
   - کنسول مرورگر را برای خطاها بررسی کنید

### لاگ‌ها

```bash
# مشاهده همه لاگ‌ها
docker-compose logs -f

# مشاهده لاگ‌های سرویس خاص
docker-compose logs -f backend
docker-compose logs -f bot
docker-compose logs -f frontend

# مشاهده آخرین 100 خط
docker-compose logs --tail=100 backend
```

### مدیریت دیتابیس

```bash
# اتصال به دیتابیس
docker-compose exec postgres psql -U telegram_bot_user -d telegram_bot_saas

# پشتیبان‌گیری دیتابیس
docker-compose exec postgres pg_dump -U telegram_bot_user telegram_bot_saas > backup.sql

# بازیابی دیتابیس
docker-compose exec -T postgres psql -U telegram_bot_user -d telegram_bot_saas < backup.sql
```

## 📄 مجوز

این پروژه تحت مجوز MIT مجوز دارد - فایل [LICENSE](LICENSE) را برای جزئیات ببینید.

## 🤝 مشارکت

1. مخزن را فورک کنید
2. شاخه ویژگی ایجاد کنید
3. تغییرات خود را اعمال کنید
4. تست‌ها را اضافه کنید
5. درخواست pull ارسال کنید

## 📞 پشتیبانی

- **مستندات**: [docs/](docs/)
- **مسائل**: [GitHub Issues](https://github.com/your-repo/issues)
- **بحث‌ها**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🎯 نقشه راه

- [ ] پشتیبانی از استقرار Kubernetes
- [ ] مانیتورینگ و هشدار پیشرفته
- [ ] پشتیبانی چندزبانه
- [ ] قالب‌های بات پیشرفته
- [ ] مجموعه تست خودکار
- [ ] بهینه‌سازی عملکرد
- [ ] اپلیکیشن موبایل برای ادمین‌ها
- [ ] داشبورد تحلیل پیشرفته

---

**موفق باشید! 🚀**