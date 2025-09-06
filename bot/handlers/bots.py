"""Bot management handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import structlog
from ..utils.api_client import APIClient

logger = structlog.get_logger()
router = Router()


@router.message(Command("mybots"))
@router.callback_query(F.data == "my_bots")
async def list_user_bots(message_or_callback, state=None):
    """List user's bot instances."""
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer()
        message = message_or_callback.message
    else:
        message = message_or_callback
    
    try:
        api_client = APIClient()
        bots = await api_client.get_user_bots()
        
        if not bots:
            text = """
📋 **Your Bots**

You don't have any bots yet.

Use /start to create your first bot!
            """
            await message.answer(text, parse_mode="Markdown")
            return
        
        text = "📋 **Your Bots**\n\n"
        
        for i, bot in enumerate(bots, 1):
            status_emoji = {
                "pending": "⏳",
                "building": "🔨",
                "running": "✅",
                "stopped": "⏹️",
                "error": "❌"
            }.get(bot["status"], "❓")
            
            text += f"{i}. **{bot['bot_name']}**\n"
            text += f"   Status: {status_emoji} {bot['status'].title()}\n"
            text += f"   Created: {bot['created_at'][:10]}\n"
            text += f"   Repo: `{bot['github_repo']}`\n\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Create New Bot", callback_data="create_bot")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="my_bots")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get user bots", error=str(e))
        await message.answer(
            "❌ Failed to load your bots. Please try again later.",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("bot_details:"))
async def show_bot_details(callback: CallbackQuery):
    """Show detailed information about a specific bot."""
    await callback.answer()
    
    bot_id = callback.data.split(":")[1]
    
    try:
        api_client = APIClient()
        bots = await api_client.get_user_bots()
        
        bot = next((b for b in bots if b["id"] == bot_id), None)
        if not bot:
            await callback.message.edit_text("❌ Bot not found.")
            return
        
        status_emoji = {
            "pending": "⏳",
            "building": "🔨",
            "running": "✅",
            "stopped": "⏹️",
            "error": "❌"
        }.get(bot["status"], "❓")
        
        text = f"""
🤖 **Bot Details**

**Name:** {bot['bot_name']}
**Status:** {status_emoji} {bot['status'].title()}
**Created:** {bot['created_at'][:19]}
**Updated:** {bot['updated_at'][:19]}

**Repository:** `{bot['github_repo']}`
**Admin ID:** `{bot['admin_numeric_id']}`
**Channel Lock:** `{bot.get('channel_lock_id', 'None')}`

**Container Info:**
• Container ID: `{bot.get('container_id', 'N/A')}`
• Container Name: `{bot.get('container_name', 'N/A')}`
• Health Status: {'✅ Healthy' if bot.get('is_healthy') else '❌ Unhealthy'}

**Logs:**
• Build Log: {bot.get('build_log', 'N/A')[:100] + '...' if bot.get('build_log') else 'N/A'}
• Error Log: {bot.get('error_log', 'N/A')[:100] + '...' if bot.get('error_log') else 'N/A'}
        """
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Back to Bots", callback_data="my_bots")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"bot_details:{bot_id}")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get bot details", error=str(e))
        await callback.message.edit_text(
            "❌ Failed to load bot details. Please try again later.",
            parse_mode="Markdown"
        )