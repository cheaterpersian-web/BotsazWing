"""Subscription plans handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import structlog
from ..utils.api_client import APIClient

logger = structlog.get_logger()
router = Router()


@router.message(Command("plans"))
@router.callback_query(F.data == "view_plans")
async def list_subscription_plans(message_or_callback, state=None):
    """List available subscription plans."""
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer()
        message = message_or_callback.message
    else:
        message = message_or_callback
    
    try:
        api_client = APIClient()
        plans = await api_client.get_subscription_plans()
        
        if not plans:
            text = """
📦 **Subscription Plans**

No subscription plans are currently available.

Please contact support for more information.
            """
            await message.answer(text, parse_mode="Markdown")
            return
        
        text = "📦 **Available Subscription Plans**\n\n"
        
        for i, plan in enumerate(plans, 1):
            duration_text = ""
            if plan["duration_days"] == 30:
                duration_text = "1 Month"
            elif plan["duration_days"] == 60:
                duration_text = "2 Months"
            elif plan["duration_days"] == 90:
                duration_text = "3 Months"
            elif plan["duration_days"] == 180:
                duration_text = "6 Months"
            elif plan["duration_days"] == 365:
                duration_text = "1 Year"
            else:
                duration_text = f"{plan['duration_days']} Days"
            
            text += f"{i}. **{plan['name']}**\n"
            text += f"   💰 Price: ${plan['price']} {plan['currency']}\n"
            text += f"   ⏱️ Duration: {duration_text}\n"
            if plan.get('description'):
                text += f"   📝 {plan['description']}\n"
            text += "\n"
        
        text += """
**Features included:**
✅ Bot deployment from GitHub
✅ Docker containerization
✅ 24/7 monitoring
✅ Automatic scaling
✅ Technical support
✅ SSL certificates
✅ Custom domains

**Payment Methods:**
🏦 Bank Transfer
₿ Cryptocurrency

Use /start to create a bot and subscribe to a plan!
        """
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Create Bot", callback_data="create_bot")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="view_plans")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get subscription plans", error=str(e))
        await message.answer(
            "❌ Failed to load subscription plans. Please try again later.",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("plan_details:"))
async def show_plan_details(callback: CallbackQuery):
    """Show detailed information about a specific plan."""
    await callback.answer()
    
    plan_id = callback.data.split(":")[1]
    
    try:
        api_client = APIClient()
        plans = await api_client.get_subscription_plans()
        
        plan = next((p for p in plans if p["id"] == plan_id), None)
        if not plan:
            await callback.message.edit_text("❌ Plan not found.")
            return
        
        duration_text = ""
        if plan["duration_days"] == 30:
            duration_text = "1 Month"
        elif plan["duration_days"] == 60:
            duration_text = "2 Months"
        elif plan["duration_days"] == 90:
            duration_text = "3 Months"
        elif plan["duration_days"] == 180:
            duration_text = "6 Months"
        elif plan["duration_days"] == 365:
            duration_text = "1 Year"
        else:
            duration_text = f"{plan['duration_days']} Days"
        
        text = f"""
📦 **Plan Details**

**Name:** {plan['name']}
**Price:** ${plan['price']} {plan['currency']}
**Duration:** {duration_text}
**Status:** {'✅ Active' if plan.get('is_active') else '❌ Inactive'}

**Description:**
{plan.get('description', 'No description available.')}

**What's included:**
✅ Bot deployment from GitHub repositories
✅ Docker containerization and orchestration
✅ 24/7 monitoring and health checks
✅ Automatic scaling based on usage
✅ Technical support via Telegram
✅ SSL certificates for webhooks
✅ Custom domain support
✅ Backup and recovery
✅ Log aggregation and analysis

**Perfect for:**
• Individual developers
• Small businesses
• Startups
• Anyone wanting to deploy Telegram bots

**Next Steps:**
1. Create a bot using /start
2. Choose this plan during setup
3. Complete payment
4. Your bot will be deployed automatically
        """
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Create Bot with This Plan", callback_data=f"create_bot_plan:{plan_id}")],
            [InlineKeyboardButton(text="📋 Back to Plans", callback_data="view_plans")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get plan details", error=str(e))
        await callback.message.edit_text(
            "❌ Failed to load plan details. Please try again later.",
            parse_mode="Markdown"
        )