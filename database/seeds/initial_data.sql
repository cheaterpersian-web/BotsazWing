-- Initial data seeds for Telegram Bot SaaS Platform
-- This file contains default data to populate the database

-- Insert default subscription plans
INSERT INTO subscription_plans (name, description, duration_days, price, currency) VALUES
('Monthly Plan', '1 month subscription for bot deployment', 30, 9.99, 'USD'),
('Bi-Monthly Plan', '2 months subscription for bot deployment', 60, 18.99, 'USD'),
('Quarterly Plan', '3 months subscription for bot deployment', 90, 26.99, 'USD'),
('Semi-Annual Plan', '6 months subscription for bot deployment', 180, 49.99, 'USD'),
('Annual Plan', '1 year subscription for bot deployment', 365, 89.99, 'USD');

-- Insert default system settings
INSERT INTO system_settings (key, value, description, is_encrypted) VALUES
('bot_deployment_timeout', '300', 'Timeout for bot deployment in seconds', false),
('max_bots_per_user', '10', 'Maximum number of bots per user', false),
('default_github_template', 'https://github.com/your-org/telegram-bot-template', 'Default GitHub template repository', false),
('payment_verification_timeout', '24', 'Hours to wait for payment verification', false),
('subscription_reminder_days', '7,3,1', 'Days before expiration to send reminders', false),
('encryption_key', '', 'Encryption key for sensitive data (set via environment)', true),
('bank_account_number', '', 'Bank account number for transfers (set via environment)', true),
('crypto_wallet_address', '', 'Crypto wallet address for payments (set via environment)', true);

-- Insert default notification templates
INSERT INTO notification_templates (name, subject, template, variables) VALUES
('subscription_expiring_7_days', 'Your bot subscription expires in 7 days', 
'Hi {{user_name}}! Your bot "{{bot_name}}" subscription will expire in 7 days. Please renew to avoid service interruption.', 
'["user_name", "bot_name", "expiration_date", "renewal_url"]'),

('subscription_expiring_3_days', 'Your bot subscription expires in 3 days', 
'Hi {{user_name}}! Your bot "{{bot_name}}" subscription will expire in 3 days. Please renew immediately to avoid service interruption.', 
'["user_name", "bot_name", "expiration_date", "renewal_url"]'),

('subscription_expiring_1_day', 'Your bot subscription expires tomorrow', 
'Hi {{user_name}}! Your bot "{{bot_name}}" subscription expires tomorrow. Please renew now to avoid service interruption.', 
'["user_name", "bot_name", "expiration_date", "renewal_url"]'),

('subscription_expired', 'Your bot subscription has expired', 
'Hi {{user_name}}! Your bot "{{bot_name}}" subscription has expired and the bot has been stopped. Please renew to reactivate.', 
'["user_name", "bot_name", "expiration_date", "renewal_url"]'),

('payment_confirmed', 'Payment confirmed - Bot activated', 
'Hi {{user_name}}! Your payment has been confirmed and your bot "{{bot_name}}" is now active until {{expiration_date}}.', 
'["user_name", "bot_name", "expiration_date"]'),

('payment_rejected', 'Payment rejected', 
'Hi {{user_name}}! Your payment for bot "{{bot_name}}" has been rejected. Please contact support for assistance.', 
'["user_name", "bot_name", "rejection_reason"]'),

('bot_deployment_success', 'Bot deployed successfully', 
'Hi {{user_name}}! Your bot "{{bot_name}}" has been deployed successfully and is now running.', 
'["user_name", "bot_name", "bot_url"]'),

('bot_deployment_failed', 'Bot deployment failed', 
'Hi {{user_name}}! Your bot "{{bot_name}}" deployment failed. Please check the logs and try again.', 
'["user_name", "bot_name", "error_message"]');