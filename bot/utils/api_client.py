"""API client for communicating with the backend."""

import httpx
from typing import Optional, Dict, Any
from ..config import settings


class APIClient:
    """Client for backend API communication."""
    
    def __init__(self):
        """Initialize API client."""
        self.base_url = settings.api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.api_token}",
            "Content-Type": "application/json"
        }
    
    async def login_user(self, telegram_user_id: int, username: str = None, 
                        first_name: str = None, last_name: str = None, 
                        language_code: str = "en") -> Dict[str, Any]:
        """Login user with Telegram data."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login/telegram",
                json={
                    "telegram_user_id": telegram_user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "language_code": language_code
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def create_bot_instance(self, bot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new bot instance."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/bots/",
                json=bot_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_bots(self) -> list[Dict[str, Any]]:
        """Get user's bot instances."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/bots/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_subscription_plans(self) -> list[Dict[str, Any]]:
        """Get available subscription plans."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/subscriptions/plans",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new subscription."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/subscriptions/",
                json=subscription_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new payment."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/payments/",
                json=payment_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def upload_receipt(self, payment_id: str, file_data: bytes, 
                           filename: str, content_type: str) -> Dict[str, Any]:
        """Upload payment receipt."""
        async with httpx.AsyncClient() as client:
            files = {
                "receipt_file": (filename, file_data, content_type)
            }
            response = await client.post(
                f"{self.base_url}/api/v1/payments/{payment_id}/receipt",
                files=files,
                headers={"Authorization": f"Bearer {settings.api_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_bank_details(self) -> Dict[str, Any]:
        """Get bank account details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/payments/bank-details/info",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_crypto_details(self) -> Dict[str, Any]:
        """Get crypto wallet details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/payments/crypto-details/info",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_payments(self) -> list[Dict[str, Any]]:
        """Get user's payments."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/payments/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()