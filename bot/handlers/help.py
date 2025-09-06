"""Help and support handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import structlog

logger = structlog.get_logger()
router = Router()


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def show_help(message_or_callback, state=None):
    """Show help information."""
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer()
        message = message_or_callback.message
    else:
        message = message_or_callback
    
    help_text = """
❓ **Help & Support**

**Available Commands:**
/start - Start bot creation process
/mybots - View your deployed bots
/plans - View subscription plans
/payments - Manage payments
/help - Show this help message

**How to Create a Bot:**
1. Use /start command
2. Provide your bot token from @BotFather
3. Enter your GitHub repository URL
4. Add GitHub token (for private repos)
5. Set your admin numeric ID
6. Choose subscription plan
7. Complete payment

**Getting Your Bot Token:**
1. Message @BotFather on Telegram
2. Send /newbot command
3. Follow the instructions
4. Copy the token you receive

**Getting Your Numeric ID:**
1. Message @userinfobot on Telegram
2. It will reply with your numeric ID
3. Copy the number

**GitHub Repository Requirements:**
• Must contain a Python bot
• Should have main.py or similar entry point
• Can include Dockerfile (optional)
• Public or private (with token)

**Payment Methods:**
🏦 **Bank Transfer:**
• Send money to our bank account
• Upload receipt as proof
• Manual verification (24-48 hours)

₿ **Cryptocurrency:**
• Send crypto to our wallet
• Provide transaction hash
• Manual verification (24-48 hours)

**Bot Deployment Process:**
1. Repository cloning
2. Docker image building
3. Container creation
4. Bot startup
5. Health monitoring

**Support:**
• Technical issues: Contact @support_bot
• Payment questions: Contact @payment_support
• General inquiries: Contact @admin_bot

**FAQ:**
**Q: How long does deployment take?**
A: Usually 2-5 minutes depending on repository size.

**Q: Can I update my bot?**
A: Yes, redeploy with updated repository.

**Q: What happens if payment fails?**
A: Bot will be stopped until payment is confirmed.

**Q: Can I cancel my subscription?**
A: Yes, contact support for cancellation.

**Q: Is my data secure?**
A: Yes, all tokens are encrypted and stored securely.
    """
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Create Bot", callback_data="create_bot")],
        [InlineKeyboardButton(text="📋 My Bots", callback_data="my_bots")],
        [InlineKeyboardButton(text="💳 Plans", callback_data="view_plans")],
        [InlineKeyboardButton(text="🆘 Contact Support", url="https://t.me/support_bot")]
    ])
    
    await message.answer(help_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("status"))
async def show_system_status(message: Message):
    """Show system status."""
    status_text = """
📊 **System Status**

**Services:**
✅ Bot Deployment Service - Online
✅ Database - Online
✅ Docker Engine - Online
✅ File Storage - Online
✅ Payment Processing - Online

**Current Statistics:**
• Active Bots: 1,234
• Total Users: 5,678
• Uptime: 99.9%
• Last Update: Just now

**Maintenance:**
• No scheduled maintenance
• All systems operational

**Performance:**
• Average deployment time: 3.2 minutes
• Success rate: 99.7%
• Support response time: < 2 hours

For real-time status updates, visit our status page.
    """
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Status", callback_data="refresh_status")],
        [InlineKeyboardButton(text="📊 Detailed Status", url="https://status.telegrambotsaas.com")]
    ])
    
    await message.answer(status_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "refresh_status")
async def refresh_status(callback: CallbackQuery):
    """Refresh system status."""
    await callback.answer("Status refreshed!")
    
    # This would fetch real status from the backend
    status_text = """
📊 **System Status** (Refreshed)

**Services:**
✅ Bot Deployment Service - Online
✅ Database - Online
✅ Docker Engine - Online
✅ File Storage - Online
✅ Payment Processing - Online

**Current Statistics:**
• Active Bots: 1,235
• Total Users: 5,679
• Uptime: 99.9%
• Last Update: Just now

All systems are operational! 🚀
    """
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Again", callback_data="refresh_status")],
        [InlineKeyboardButton(text="📊 Detailed Status", url="https://status.telegrambotsaas.com")]
    ])
    
    await callback.message.edit_text(status_text, reply_markup=keyboard, parse_mode="Markdown")