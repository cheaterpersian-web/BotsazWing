-- Database initialization script
-- This script sets up the database and runs migrations

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE telegram_bot_saas'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'telegram_bot_saas')\gexec

-- Connect to the database
\c telegram_bot_saas;

-- Run initial schema migration
\i migrations/001_initial_schema.sql

-- Run initial data seeds
\i seeds/initial_data.sql

-- Create a read-only user for monitoring
CREATE USER telegram_bot_monitor WITH PASSWORD 'monitor_password';
GRANT CONNECT ON DATABASE telegram_bot_saas TO telegram_bot_monitor;
GRANT USAGE ON SCHEMA public TO telegram_bot_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO telegram_bot_monitor;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO telegram_bot_monitor;

-- Create a backup user
CREATE USER telegram_bot_backup WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE telegram_bot_saas TO telegram_bot_backup;
GRANT USAGE ON SCHEMA public TO telegram_bot_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO telegram_bot_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO telegram_bot_backup;