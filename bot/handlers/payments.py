"""Payment management handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import structlog
from ..utils.api_client import APIClient
from ..utils.validators import validate_payment_amount, validate_transaction_hash, validate_bank_reference

logger = structlog.get_logger()
router = Router()


class PaymentStates(StatesGroup):
    """States for payment flow."""
    waiting_for_payment_method = State()
    waiting_for_amount = State()
    waiting_for_receipt = State()
    waiting_for_transaction_hash = State()


@router.message(Command("payments"))
@router.callback_query(F.data == "view_payments")
async def list_user_payments(message_or_callback, state=None):
    """List user's payments."""
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer()
        message = message_or_callback.message
    else:
        message = message_or_callback
    
    try:
        api_client = APIClient()
        payments = await api_client.get_user_payments()
        
        if not payments:
            text = """
💳 **Your Payments**

You don't have any payments yet.

Create a bot and subscribe to a plan to make your first payment!
            """
            await message.answer(text, parse_mode="Markdown")
            return
        
        text = "💳 **Your Payments**\n\n"
        
        for i, payment in enumerate(payments, 1):
            status_emoji = {
                "pending": "⏳",
                "confirmed": "✅",
                "rejected": "❌",
                "cancelled": "🚫"
            }.get(payment["status"], "❓")
            
            text += f"{i}. **Payment #{payment['id'][:8]}**\n"
            text += f"   Amount: ${payment['amount']} {payment['currency']}\n"
            text += f"   Method: {payment['payment_method'].replace('_', ' ').title()}\n"
            text += f"   Status: {status_emoji} {payment['status'].title()}\n"
            text += f"   Created: {payment['created_at'][:10]}\n\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="view_payments")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get user payments", error=str(e))
        await message.answer(
            "❌ Failed to load your payments. Please try again later.",
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "make_payment")
async def start_payment_process(callback: CallbackQuery, state: FSMContext):
    """Start payment process."""
    await callback.answer()
    await state.set_state(PaymentStates.waiting_for_payment_method)
    
    text = """
💳 **Payment Method**

Choose your preferred payment method:

**Bank Transfer:**
• Send money to our bank account
• Upload receipt as proof
• Manual verification (24-48 hours)

**Cryptocurrency:**
• Send crypto to our wallet
• Provide transaction hash
• Manual verification (24-48 hours)
    """
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏦 Bank Transfer", callback_data="payment_method:bank_transfer")],
        [InlineKeyboardButton(text="₿ Cryptocurrency", callback_data="payment_method:crypto")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("payment_method:"))
async def select_payment_method(callback: CallbackQuery, state: FSMContext):
    """Handle payment method selection."""
    await callback.answer()
    
    payment_method = callback.data.split(":")[1]
    await state.update_data(payment_method=payment_method)
    
    if payment_method == "bank_transfer":
        await state.set_state(PaymentStates.waiting_for_amount)
        
        # Get bank details
        api_client = APIClient()
        try:
            bank_details = await api_client.get_bank_details()
            
            text = f"""
🏦 **Bank Transfer Payment**

**Bank Details:**
• Bank: {bank_details['bank_name']}
• Account Number: `{bank_details['account_number']}`
• Account Holder: {bank_details['account_holder']}
• Routing Number: `{bank_details['routing_number']}`
• SWIFT Code: `{bank_details['swift_code']}`

**Instructions:**
{bank_details['instructions']}

**Next Steps:**
1. Send the payment to the account above
2. Include the reference code in the transfer description
3. Upload the receipt as proof

Please enter the amount you're paying:
            """
            
            await callback.message.edit_text(text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error("Failed to get bank details", error=str(e))
            await callback.message.edit_text(
                "❌ Failed to load bank details. Please try again later.",
                parse_mode="Markdown"
            )
    
    elif payment_method == "crypto":
        await state.set_state(PaymentStates.waiting_for_amount)
        
        # Get crypto details
        api_client = APIClient()
        try:
            crypto_details = await api_client.get_crypto_details()
            
            text = f"""
₿ **Cryptocurrency Payment**

**Wallet Details:**
• Currency: {crypto_details['currency']}
• Wallet Address: `{crypto_details['wallet_address']}`

**Instructions:**
{crypto_details['instructions']}

**Next Steps:**
1. Send the exact amount to the wallet above
2. Provide the transaction hash as proof

Please enter the amount you're paying:
            """
            
            await callback.message.edit_text(text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error("Failed to get crypto details", error=str(e))
            await callback.message.edit_text(
                "❌ Failed to load crypto details. Please try again later.",
                parse_mode="Markdown"
            )


@router.message(PaymentStates.waiting_for_amount)
async def process_payment_amount(message: Message, state: FSMContext):
    """Process payment amount."""
    amount = validate_payment_amount(message.text)
    
    if not amount:
        await message.answer(
            "❌ Invalid amount. Please enter a valid number greater than 0.\n\n"
            "Example: 9.99",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(amount=amount)
    data = await state.get_data()
    
    if data["payment_method"] == "bank_transfer":
        await state.set_state(PaymentStates.waiting_for_receipt)
        
        text = f"""
📄 **Upload Receipt**

Amount: ${amount}
Payment Method: Bank Transfer

Please upload a photo of your bank transfer receipt.

**Make sure the receipt shows:**
• Transfer amount
• Recipient account details
• Reference code
• Date and time
        """
        
        await message.answer(text, parse_mode="Markdown")
    
    elif data["payment_method"] == "crypto":
        await state.set_state(PaymentStates.waiting_for_transaction_hash)
        
        text = f"""
🔗 **Transaction Hash**

Amount: ${amount}
Payment Method: Cryptocurrency

Please provide the transaction hash from your crypto transfer.

**Example:** `a1b2c3d4e5f6...` (64 characters)
        """
        
        await message.answer(text, parse_mode="Markdown")


@router.message(PaymentStates.waiting_for_receipt)
async def process_payment_receipt(message: Message, state: FSMContext):
    """Process payment receipt upload."""
    if not message.photo:
        await message.answer(
            "❌ Please upload a photo of your bank transfer receipt.",
            parse_mode="Markdown"
        )
        return
    
    # Get the largest photo
    photo = message.photo[-1]
    
    try:
        # Download photo
        file = await message.bot.get_file(photo.file_id)
        file_data = await message.bot.download_file(file.file_path)
        
        data = await state.get_data()
        
        # Create payment record
        api_client = APIClient()
        payment_data = {
            "subscription_id": "temp",  # This should come from context
            "amount": data["amount"],
            "currency": "USD",
            "payment_method": data["payment_method"]
        }
        
        payment = await api_client.create_payment(payment_data)
        
        # Upload receipt
        await api_client.upload_receipt(
            payment["id"],
            file_data.read(),
            f"receipt_{payment['id']}.jpg",
            "image/jpeg"
        )
        
        success_text = f"""
✅ **Payment Submitted Successfully!**

**Payment Details:**
• Amount: ${data['amount']}
• Method: Bank Transfer
• Status: Pending Verification
• Payment ID: `{payment['id'][:8]}`

**What happens next:**
1. Our team will verify your payment
2. You'll receive a notification when confirmed
3. Your bot will be activated automatically

**Verification time:** 24-48 hours

Use /payments to check your payment status.
        """
        
        await message.answer(success_text, parse_mode="Markdown")
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to process payment receipt", error=str(e))
        await message.answer(
            "❌ Failed to process payment. Please try again later.\n\nError: {}".format(str(e)),
            parse_mode="Markdown"
        )
        await state.clear()


@router.message(PaymentStates.waiting_for_transaction_hash)
async def process_transaction_hash(message: Message, state: FSMContext):
    """Process cryptocurrency transaction hash."""
    tx_hash = message.text.strip()
    
    if not validate_transaction_hash(tx_hash):
        await message.answer(
            "❌ Invalid transaction hash format.\n\n"
            "Please provide a valid transaction hash:\n"
            "• Bitcoin: 64 hex characters\n"
            "• Ethereum: 66 characters starting with 0x",
            parse_mode="Markdown"
        )
        return
    
    try:
        data = await state.get_data()
        
        # Create payment record
        api_client = APIClient()
        payment_data = {
            "subscription_id": "temp",  # This should come from context
            "amount": data["amount"],
            "currency": "USD",
            "payment_method": data["payment_method"],
            "transaction_hash": tx_hash
        }
        
        payment = await api_client.create_payment(payment_data)
        
        success_text = f"""
✅ **Payment Submitted Successfully!**

**Payment Details:**
• Amount: ${data['amount']}
• Method: Cryptocurrency
• Transaction Hash: `{tx_hash[:20]}...`
• Status: Pending Verification
• Payment ID: `{payment['id'][:8]}`

**What happens next:**
1. Our team will verify your transaction
2. You'll receive a notification when confirmed
3. Your bot will be activated automatically

**Verification time:** 24-48 hours

Use /payments to check your payment status.
        """
        
        await message.answer(success_text, parse_mode="Markdown")
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to process payment", error=str(e))
        await message.answer(
            "❌ Failed to process payment. Please try again later.\n\nError: {}".format(str(e)),
            parse_mode="Markdown"
        )
        await state.clear()


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment process."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Payment cancelled.")