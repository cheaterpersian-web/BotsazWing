# API Documentation

## Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### Authentication

#### Login (Telegram)
```http
POST /auth/login/telegram
```

**Request Body:**
```json
{
  "telegram_user_id": 123456789,
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "language_code": "en"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Admin Login
```http
POST /auth/login/admin
```

**Request Body:**
```json
{
  "telegram_user_id": 123456789,
  "username": "admin",
  "first_name": "Admin",
  "last_name": "User"
}
```

#### Get Current User
```http
GET /auth/me
```

**Response:**
```json
{
  "id": "uuid",
  "telegram_user_id": 123456789,
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Users

#### List Users (Admin Only)
```http
GET /users/?page=1&size=10
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "telegram_user_id": 123456789,
      "username": "username",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

#### Get User
```http
GET /users/{user_id}
```

#### Update User
```http
PUT /users/{user_id}
```

**Request Body:**
```json
{
  "username": "new_username",
  "first_name": "New Name",
  "is_active": true
}
```

#### Delete User (Admin Only)
```http
DELETE /users/{user_id}
```

### Bot Instances

#### Create Bot Instance
```http
POST /bots/
```

**Request Body:**
```json
{
  "bot_name": "My Bot",
  "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "github_repo": "https://github.com/user/my-bot",
  "github_token": "ghp_xxxxxxxxxxxx",
  "admin_numeric_id": 123456789,
  "channel_lock_id": -1001234567890
}
```

**Response:**
```json
{
  "id": "uuid",
  "bot_name": "My Bot",
  "status": "pending",
  "github_repo": "https://github.com/user/my-bot",
  "admin_numeric_id": 123456789,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### List User's Bots
```http
GET /bots/
```

#### List All Bots (Admin Only)
```http
GET /bots/all?page=1&size=10
```

#### Get Bot Instance
```http
GET /bots/{bot_id}
```

#### Update Bot Instance
```http
PUT /bots/{bot_id}
```

#### Delete Bot Instance
```http
DELETE /bots/{bot_id}
```

#### Start Bot (Admin Only)
```http
POST /bots/{bot_id}/start
```

#### Stop Bot (Admin Only)
```http
POST /bots/{bot_id}/stop
```

#### Restart Bot (Admin Only)
```http
POST /bots/{bot_id}/restart
```

### Subscriptions

#### Get Subscription Plans
```http
GET /subscriptions/plans
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Monthly Plan",
    "description": "1 month subscription",
    "duration_days": 30,
    "price": 9.99,
    "currency": "USD",
    "is_active": true
  }
]
```

#### Create Subscription Plan (Admin Only)
```http
POST /subscriptions/plans
```

**Request Body:**
```json
{
  "name": "Custom Plan",
  "description": "Custom subscription plan",
  "duration_days": 45,
  "price": 14.99,
  "currency": "USD"
}
```

#### Update Subscription Plan (Admin Only)
```http
PUT /subscriptions/plans/{plan_id}
```

#### Delete Subscription Plan (Admin Only)
```http
DELETE /subscriptions/plans/{plan_id}
```

#### Create Subscription
```http
POST /subscriptions/
```

**Request Body:**
```json
{
  "bot_instance_id": "uuid",
  "plan_id": "uuid",
  "start_at": "2024-01-01T00:00:00Z",
  "end_at": "2024-02-01T00:00:00Z"
}
```

#### List User's Subscriptions
```http
GET /subscriptions/
```

#### List All Subscriptions (Admin Only)
```http
GET /subscriptions/all?page=1&size=10
```

#### Get Subscription
```http
GET /subscriptions/{subscription_id}
```

#### Update Subscription (Admin Only)
```http
PUT /subscriptions/{subscription_id}
```

#### Extend Subscription (Admin Only)
```http
POST /subscriptions/{subscription_id}/extend?days=30
```

#### Get Expiring Subscriptions (Admin Only)
```http
GET /subscriptions/expiring/reminders?days=7
```

#### Get Expired Subscriptions (Admin Only)
```http
GET /subscriptions/expired/list
```

### Payments

#### Create Payment
```http
POST /payments/
```

**Request Body:**
```json
{
  "subscription_id": "uuid",
  "amount": 9.99,
  "currency": "USD",
  "payment_method": "bank_transfer",
  "transaction_hash": "a1b2c3d4e5f6...",
  "bank_reference": "TB20240101001"
}
```

#### Upload Payment Receipt
```http
POST /payments/{payment_id}/receipt
```

**Request:** Multipart form data with `receipt_file`

#### List User's Payments
```http
GET /payments/
```

#### List All Payments (Admin Only)
```http
GET /payments/all?page=1&size=10&status_filter=pending
```

#### Get Pending Payments (Admin Only)
```http
GET /payments/pending
```

#### Get Payment
```http
GET /payments/{payment_id}
```

#### Update Payment (Admin Only)
```http
PUT /payments/{payment_id}
```

**Request Body:**
```json
{
  "status": "confirmed",
  "admin_notes": "Payment verified successfully"
}
```

#### Confirm Payment (Admin Only)
```http
POST /payments/{payment_id}/confirm
```

#### Reject Payment (Admin Only)
```http
POST /payments/{payment_id}/reject?reason=Invalid receipt
```

#### Get Bank Details
```http
GET /payments/bank-details/info
```

**Response:**
```json
{
  "bank_name": "Example Bank",
  "account_number": "1234567890",
  "account_holder": "Telegram Bot SaaS",
  "routing_number": "123456789",
  "swift_code": "EXAMPLUS",
  "instructions": "Please include the reference code in the transfer description"
}
```

#### Get Crypto Details
```http
GET /payments/crypto-details/info
```

**Response:**
```json
{
  "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
  "currency": "BTC",
  "instructions": "Please send the exact amount and include the transaction hash"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate limited:
- General endpoints: 100 requests per minute
- Bot webhook: 5 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

### Telegram Bot Webhook
```http
POST /webhook/{bot_token}
```

This endpoint receives updates from Telegram for the main bot.

## Pagination

List endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `size`: Items per page (default: 10, max: 100)

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

## Filtering

Some endpoints support filtering:
- Payments: `status_filter` (pending, confirmed, rejected, cancelled)
- Users: Filter by active/inactive status
- Bots: Filter by status (pending, building, running, stopped, error)

## Sorting

List endpoints return results sorted by creation date (newest first) by default.

## File Uploads

File uploads are supported for:
- Payment receipts (images)
- Build logs
- Bot configuration files

Maximum file size: 50MB
Supported formats: Images (JPEG, PNG, GIF), Text files, Archives

## WebSocket Support

Real-time updates are available via WebSocket connections for:
- Bot deployment status
- Payment confirmations
- System notifications

WebSocket endpoint: `ws://localhost:8000/ws`