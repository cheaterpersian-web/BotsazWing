# Telegram Bot SaaS Platform

A professional Telegram-based SaaS platform where users can deploy their own bots from GitHub repositories with subscription-based access.

## Features

- **Multi-tenant Bot Deployment**: Deploy bots from GitHub repositories with Docker containers
- **Subscription Management**: Monthly, bi-monthly, and custom subscription plans
- **Payment Processing**: Bank transfer and crypto payment support with manual verification
- **Admin Dashboard**: Web-based admin panel for managing users, bots, and subscriptions
- **Automated Management**: Cron jobs for subscription checks and container lifecycle management
- **Security**: Encrypted token storage and comprehensive security measures

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL database
- **Telegram Bot**: aiogram-based bot for user interaction
- **Frontend**: React admin dashboard with TailwindCSS and shadcn/ui
- **Containerization**: Docker with docker-compose for orchestration
- **Background Jobs**: Celery for async tasks and cron jobs
- **Storage**: MinIO for file storage (receipts, logs)
- **Monitoring**: Sentry for error tracking

## Quick Start

1. Clone the repository
2. Run the installation script: `./install.sh`
3. Configure environment variables in `.env`
4. Start services: `docker-compose up -d`

## Project Structure

```
├── backend/           # FastAPI backend service
├── frontend/          # React admin dashboard
├── bot/              # aiogram Telegram bot
├── database/         # PostgreSQL schema and migrations
├── scripts/          # Installation and utility scripts
├── docker-compose.yml # Service orchestration
└── docs/            # Documentation
```

## License

MIT License