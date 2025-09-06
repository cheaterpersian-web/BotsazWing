# Telegram Bot SaaS Platform

A professional Telegram-based SaaS platform where users can deploy their own bots from GitHub repositories with subscription-based access.

## 🚀 Features

- **Multi-tenant Bot Deployment**: Deploy bots from GitHub repositories with Docker containers
- **Subscription Management**: Monthly, bi-monthly, and custom subscription plans
- **Payment Processing**: Bank transfer and crypto payment support with manual verification
- **Admin Dashboard**: Web-based admin panel for managing users, bots, and subscriptions
- **Automated Management**: Cron jobs for subscription checks and container lifecycle management
- **Security**: Encrypted token storage and comprehensive security measures
- **Monitoring**: Built-in monitoring with Prometheus and Grafana
- **Scalability**: Docker-based architecture for easy scaling

## 🏗️ Architecture

### Backend Services
- **FastAPI Backend**: REST API with PostgreSQL database
- **Telegram Bot**: aiogram-based bot for user interaction
- **Celery Workers**: Background task processing
- **Redis**: Caching and session storage
- **MinIO**: File storage for receipts and logs

### Frontend
- **React Admin Dashboard**: Modern web interface with TailwindCSS
- **JWT Authentication**: Secure admin access
- **Real-time Updates**: Live status monitoring

### Infrastructure
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Primary database
- **Prometheus + Grafana**: Monitoring and alerting

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- 4GB+ RAM
- 20GB+ disk space
- Linux/macOS/Windows with WSL2

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-bot-saas
   ```

2. **Run the installation script**
   ```bash
   ./install.sh
   ```

3. **Configure your bot token**
   ```bash
   # Edit .env file
   nano .env
   
   # Update TELEGRAM_BOT_TOKEN with your bot token from @BotFather
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

4. **Restart services**
   ```bash
   docker-compose restart
   ```

### Manual Installation

1. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize database**
   ```bash
   docker-compose exec postgres psql -U telegram_bot_user -d telegram_bot_saas -f /docker-entrypoint-initdb.d/init.sql
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather | Required |
| `POSTGRES_PASSWORD` | Database password | Auto-generated |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `ENCRYPTION_KEY` | Token encryption key | Auto-generated |
| `ADMIN_TELEGRAM_IDS` | Comma-separated admin IDs | Required |
| `BANK_ACCOUNT_NUMBER` | Bank account for payments | Required |
| `CRYPTO_WALLET_ADDRESS` | Crypto wallet for payments | Required |

### Admin Setup

1. **Get your Telegram ID**
   - Message @userinfobot on Telegram
   - Copy your numeric ID

2. **Add admin ID to .env**
   ```bash
   ADMIN_TELEGRAM_IDS=123456789,987654321
   ```

3. **Restart services**
   ```bash
   docker-compose restart
   ```

## 📱 Usage

### For Users

1. **Start the bot**
   - Find your bot on Telegram
   - Send `/start` command

2. **Create a bot**
   - Follow the guided setup process
   - Provide your bot token from @BotFather
   - Enter GitHub repository URL
   - Choose subscription plan
   - Complete payment

3. **Manage your bots**
   - Use `/mybots` to view your deployed bots
   - Check status and logs
   - Renew subscriptions

### For Admins

1. **Access admin dashboard**
   - Navigate to `http://localhost:3000`
   - Login with your Telegram credentials

2. **Manage platform**
   - View user statistics
   - Approve/reject payments
   - Monitor bot deployments
   - Manage subscriptions

## 🔌 API Documentation

### Authentication

All API endpoints require JWT authentication:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/
```

### Key Endpoints

- `GET /api/v1/users/` - List users
- `GET /api/v1/bots/` - List bot instances
- `POST /api/v1/bots/` - Create bot instance
- `GET /api/v1/subscriptions/` - List subscriptions
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/{id}/confirm` - Confirm payment

Full API documentation available at: `http://localhost:8000/docs`

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI application |
| Frontend | 3000 | React admin dashboard |
| Bot Webhook | 8080 | Telegram bot webhook |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache and sessions |
| MinIO | 9000/9001 | File storage |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Monitoring dashboard |
| Nginx | 80/443 | Reverse proxy |

## 📊 Monitoring

### Grafana Dashboard
- URL: `http://localhost:3001`
- Username: `admin`
- Password: Check `.env` file

### Prometheus Metrics
- URL: `http://localhost:9090`
- Endpoints: `/metrics` on all services

### Health Checks
- Backend: `http://localhost:8000/health`
- Bot: `http://localhost:8080/health`
- Frontend: `http://localhost:3000`

## 🔒 Security

### Data Protection
- All sensitive tokens are encrypted at rest
- JWT tokens for API authentication
- Rate limiting on all endpoints
- Input validation and sanitization

### Network Security
- Internal Docker network isolation
- Nginx reverse proxy with security headers
- HTTPS support (configure SSL certificates)

### Access Control
- Admin-only access to management features
- User isolation for bot deployments
- Secure file upload handling

## 🚀 Deployment

### Production Deployment

1. **Configure SSL**
   ```bash
   # Add SSL certificates to nginx/ssl/
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

2. **Update environment**
   ```bash
   # Set production values in .env
   DEBUG=false
   TELEGRAM_WEBHOOK_URL=https://yourdomain.com
   ```

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Scaling

- **Horizontal scaling**: Add more backend/bot instances
- **Database scaling**: Use PostgreSQL clustering
- **File storage**: Use external S3-compatible storage
- **Load balancing**: Configure Nginx upstream servers

## 🛠️ Development

### Local Development

1. **Start development services**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

2. **Run tests**
   ```bash
   # Backend tests
   docker-compose exec backend pytest
   
   # Frontend tests
   docker-compose exec frontend npm test
   ```

3. **Code formatting**
   ```bash
   # Backend
   docker-compose exec backend black .
   docker-compose exec backend isort .
   
   # Frontend
   docker-compose exec frontend npm run format
   ```

### Adding Features

1. **Backend API**
   - Add routes in `backend/app/api/`
   - Update schemas in `backend/app/schemas.py`
   - Add CRUD operations in `backend/app/crud.py`

2. **Frontend**
   - Add pages in `frontend/src/pages/`
   - Update API client in `frontend/src/services/api.ts`
   - Add components in `frontend/src/components/`

3. **Bot**
   - Add handlers in `bot/handlers/`
   - Update middleware in `bot/middleware/`
   - Add utilities in `bot/utils/`

## 📝 API Examples

### Create Bot Instance

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

### Confirm Payment

```bash
curl -X POST "http://localhost:8000/api/v1/payments/123e4567-e89b-12d3-a456-426614174000/confirm" \
  -H "Authorization: Bearer <admin-token>"
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token in `.env`
   - Verify webhook URL configuration
   - Check bot container logs: `docker-compose logs bot`

2. **Database connection errors**
   - Ensure PostgreSQL is running: `docker-compose ps postgres`
   - Check database credentials in `.env`
   - Verify network connectivity

3. **Payment verification issues**
   - Check MinIO service: `docker-compose logs minio`
   - Verify file upload permissions
   - Check payment status in admin dashboard

4. **Frontend not loading**
   - Check React build: `docker-compose logs frontend`
   - Verify API connectivity
   - Check browser console for errors

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f bot
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Database Management

```bash
# Connect to database
docker-compose exec postgres psql -U telegram_bot_user -d telegram_bot_saas

# Backup database
docker-compose exec postgres pg_dump -U telegram_bot_user telegram_bot_saas > backup.sql

# Restore database
docker-compose exec -T postgres psql -U telegram_bot_user -d telegram_bot_saas < backup.sql
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🎯 Roadmap

- [ ] Kubernetes deployment support
- [ ] Advanced monitoring and alerting
- [ ] Multi-language support
- [ ] Advanced bot templates
- [ ] Automated testing suite
- [ ] Performance optimization
- [ ] Mobile app for admins
- [ ] Advanced analytics dashboard