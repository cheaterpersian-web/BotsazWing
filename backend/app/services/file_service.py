"""File service for handling file uploads and storage."""

import os
import uuid
from typing import Optional
import aiofiles
from minio import Minio
from minio.error import S3Error
from ..config import settings

class FileService:
    """Service for file operations using MinIO."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"Failed to create bucket: {e}")
    
    async def upload_receipt(self, file, payment_id: uuid.UUID) -> str:
        """Upload payment receipt."""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            filename = f"receipts/{payment_id}/{uuid.uuid4()}{file_extension}"
            
            # Read file content
            content = await file.read()
            
            # Upload to MinIO
            self.client.put_object(
                self.bucket_name,
                filename,
                file,
                length=len(content),
                content_type=file.content_type or "application/octet-stream"
            )
            
            # Return URL
            return f"{settings.minio_endpoint}/{self.bucket_name}/{filename}"
            
        except Exception as e:
            raise Exception(f"Failed to upload receipt: {e}")
    
    async def upload_build_log(self, content: str, bot_instance_id: uuid.UUID) -> str:
        """Upload build log."""
        try:
            filename = f"build-logs/{bot_instance_id}/{uuid.uuid4()}.log"
            
            # Upload to MinIO
            self.client.put_object(
                self.bucket_name,
                filename,
                content.encode('utf-8'),
                length=len(content.encode('utf-8')),
                content_type="text/plain"
            )
            
            return f"{settings.minio_endpoint}/{self.bucket_name}/{filename}"
            
        except Exception as e:
            raise Exception(f"Failed to upload build log: {e}")
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from MinIO."""
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read()
        except S3Error as e:
            raise Exception(f"Failed to download file: {e}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error as e:
            raise Exception(f"Failed to delete file: {e}")
    
    async def list_files(self, prefix: str = "") -> list:
        """List files with given prefix."""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise Exception(f"Failed to list files: {e}")
    
    async def get_file_url(self, file_path: str, expires_in_seconds: int = 3600) -> str:
        """Get presigned URL for file access."""
        try:
            return self.client.presigned_get_object(
                self.bucket_name, 
                file_path, 
                expires_in_seconds
            )
        except S3Error as e:
            raise Exception(f"Failed to generate file URL: {e}")