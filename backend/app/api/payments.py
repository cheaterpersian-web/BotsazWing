"""Payment management API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import PaymentCRUD, SubscriptionCRUD, BotInstanceCRUD
from ..schemas import Payment, PaymentCreate, PaymentUpdate, PaginatedResponse
from ..api.dependencies import get_current_user, get_current_admin, require_manage_payments
from ..services.file_service import FileService
from ..security import generate_reference_code
from ..schemas import User

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=Payment)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payment."""
    # Verify subscription exists and belongs to user
    subscription = await SubscriptionCRUD.get_by_id(db, payment_data.subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Generate reference code for bank transfers
    if payment_data.payment_method == "bank_transfer":
        payment_data.bank_reference = generate_reference_code()
    
    return await PaymentCRUD.create(db, payment_data, current_user.id)


@router.post("/{payment_id}/receipt", response_model=Payment)
async def upload_payment_receipt(
    payment_id: uuid.UUID,
    receipt_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload payment receipt."""
    # Verify payment exists and belongs to user
    payment = await PaymentCRUD.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is not pending"
        )
    
    # Upload file
    file_service = FileService()
    try:
        receipt_url = await file_service.upload_receipt(receipt_file, payment_id)
        
        # Update payment with receipt URL
        updated_payment = await PaymentCRUD.update(
            db, payment_id, PaymentUpdate(receipt_url=receipt_url)
        )
        
        return updated_payment
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload receipt: {str(e)}"
        )


@router.get("/", response_model=List[Payment])
async def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's payments."""
    # This would need a new CRUD method to get payments by user
    # For now, we'll get all payments and filter
    all_payments = await PaymentCRUD.list_payments(db, skip=0, limit=1000)
    return [payment for payment in all_payments if payment.user_id == current_user.id]


@router.get("/all", response_model=PaginatedResponse)
async def list_all_payments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None, pattern="^(pending|confirmed|rejected|cancelled)$"),
    current_admin: User = Depends(require_manage_payments),
    db: AsyncSession = Depends(get_db)
):
    """List all payments (admin only)."""
    skip = (page - 1) * size
    payments = await PaymentCRUD.list_payments(db, skip=skip, limit=size, status=status_filter)
    
    # Get total count
    total = len(await PaymentCRUD.list_payments(db, skip=0, limit=1000, status=status_filter))
    
    return PaginatedResponse(
        items=payments,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/pending", response_model=List[Payment])
async def get_pending_payments(
    current_admin: User = Depends(require_manage_payments),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending payments (admin only)."""
    return await PaymentCRUD.get_pending_payments(db)


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
    payment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment by ID."""
    payment = await PaymentCRUD.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check ownership or admin access
    if payment.user_id != current_user.id:
        try:
            admin = await get_current_admin()
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return payment


@router.put("/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: uuid.UUID,
    payment_data: PaymentUpdate,
    current_admin: User = Depends(require_manage_payments),
    db: AsyncSession = Depends(get_db)
):
    """Update payment (admin only)."""
    updated_payment = await PaymentCRUD.update(
        db, payment_id, payment_data, confirmed_by=current_admin.id
    )
    if not updated_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return updated_payment


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: uuid.UUID,
    current_admin: User = Depends(require_manage_payments),
    db: AsyncSession = Depends(get_db)
):
    """Confirm a payment (admin only)."""
    confirmed_payment = await PaymentCRUD.confirm_payment(db, payment_id, current_admin.id)
    if not confirmed_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return {
        "message": "Payment confirmed successfully",
        "payment": confirmed_payment
    }


@router.post("/{payment_id}/reject")
async def reject_payment(
    payment_id: uuid.UUID,
    reason: str = Query(..., min_length=1, max_length=500),
    current_admin: User = Depends(require_manage_payments),
    db: AsyncSession = Depends(get_db)
):
    """Reject a payment (admin only)."""
    payment = await PaymentCRUD.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is not pending"
        )
    
    # Update payment status
    updated_payment = await PaymentCRUD.update(
        db, payment_id, 
        PaymentUpdate(status="rejected", admin_notes=reason),
        confirmed_by=current_admin.id
    )
    
    return {
        "message": "Payment rejected successfully",
        "payment": updated_payment
    }


@router.get("/bank-details/info")
async def get_bank_details():
    """Get bank account details for transfers."""
    # This should come from system settings
    return {
        "bank_name": "Example Bank",
        "account_number": "1234567890",
        "account_holder": "Telegram Bot SaaS",
        "routing_number": "123456789",
        "swift_code": "EXAMPLUS",
        "instructions": "Please include the reference code in the transfer description"
    }


@router.get("/crypto-details/info")
async def get_crypto_details():
    """Get crypto wallet details for payments."""
    # This should come from system settings
    return {
        "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Example Bitcoin address
        "currency": "BTC",
        "instructions": "Please send the exact amount and include the transaction hash"
    }