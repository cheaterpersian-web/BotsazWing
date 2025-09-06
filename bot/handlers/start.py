"""Start command handler."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import structlog
from ..utils.api_client import APIClient
from ..utils.validators import (
    validate_bot_token, validate_github_repo, validate_github_token,
    validate_admin_id, validate_channel_id, sanitize_input
)

logger = structlog.get_logger()
router = Router()


class BotCreationStates(StatesGroup):
    """States for bot creation flow."""
    waiting_for_bot_token = State()
    waiting_for_github_repo = State()
    waiting_for_github_token = State()
    waiting_for_admin_id = State()
    waiting_for_channel_id = State()
    confirming_creation = State()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Handle /start command."""
    await state.clear()
    
    welcome_text = """
🤖 **Welcome to Telegram Bot SaaS Platform!**

I help you deploy and manage your own Telegram bots from GitHub repositories.

**What you can do:**
• Deploy bots from GitHub repositories
• Manage subscriptions and payments
• Monitor bot performance
• Scale your bot infrastructure

**Available commands:**
/start - Start bot creation process
/mybots - View your deployed bots
/plans - View subscription plans
/payments - Manage payments
/help - Get help

Let's create your first bot! Click the button below to begin.
    """
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Create New Bot", callback_data="create_bot")],
        [InlineKeyboardButton(text="📋 My Bots", callback_data="my_bots")],
        [InlineKeyboardButton(text="💳 Subscription Plans", callback_data="view_plans")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "create_bot")
async def start_bot_creation(callback: CallbackQuery, state: FSMContext):
    """Start bot creation process."""
    await callback.answer()
    await state.set_state(BotCreationStates.waiting_for_bot_token)
    
    text = """
🔑 **Step 1: Bot Token**

Please provide your Telegram bot token.

**How to get a bot token:**
1. Message @BotFather on Telegram
2. Send /newbot command
3. Follow the instructions
4. Copy the token you receive

**Example:** `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

Send your bot token now:
    """
    
    await callback.message.edit_text(text, parse_mode="Markdown")


@router.message(BotCreationStates.waiting_for_bot_token)
async def process_bot_token(message: Message, state: FSMContext):
    """Process bot token input."""
    bot_token = sanitize_input(message.text)
    
    if not validate_bot_token(bot_token):
        await message.answer(
            "❌ Invalid bot token format. Please provide a valid token.\n\n"
            "Format should be: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(bot_token=bot_token)
    await state.set_state(BotCreationStates.waiting_for_github_repo)
    
    text = """
📁 **Step 2: GitHub Repository**

Please provide the GitHub repository URL for your bot.

**Supported formats:**
• `https://github.com/username/repository`
• `git@github.com:username/repository.git`
• `github.com/username/repository`

**Requirements:**
• Repository must contain a Python bot
• Should have a `main.py` or similar entry point
• Can include a `Dockerfile` (optional)

Send your GitHub repository URL now:
    """
    
    await message.answer(text, parse_mode="Markdown")


@router.message(BotCreationStates.waiting_for_github_repo)
async def process_github_repo(message: Message, state: FSMContext):
    """Process GitHub repository input."""
    github_repo = sanitize_input(message.text)
    
    if not validate_github_repo(github_repo):
        await message.answer(
            "❌ Invalid GitHub repository URL. Please provide a valid URL.\n\n"
            "Supported formats:\n"
            "• `https://github.com/username/repository`\n"
            "• `git@github.com:username/repository.git`\n"
            "• `github.com/username/repository`",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(github_repo=github_repo)
    await state.set_state(BotCreationStates.waiting_for_github_token)
    
    text = """
🔐 **Step 3: GitHub Token (Optional)**

If your repository is private, please provide a GitHub personal access token.

**How to create a GitHub token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (for private repos)
4. Copy the token

**If your repository is public, just send "skip" or "public".**

Send your GitHub token or "skip":
    """
    
    await message.answer(text, parse_mode="Markdown")


@router.message(BotCreationStates.waiting_for_github_token)
async def process_github_token(message: Message, state: FSMContext):
    """Process GitHub token input."""
    github_token = sanitize_input(message.text)
    
    if github_token.lower() in ["skip", "public", "none", ""]:
        github_token = None
    elif not validate_github_token(github_token):
        await message.answer(
            "❌ Invalid GitHub token format. Please provide a valid token or send 'skip' for public repositories.",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(github_token=github_token)
    await state.set_state(BotCreationStates.waiting_for_admin_id)
    
    text = """
👤 **Step 4: Admin Numeric ID**

Please provide your Telegram numeric ID (this will be the admin of your bot).

**How to get your numeric ID:**
1. Message @userinfobot on Telegram
2. It will reply with your numeric ID
3. Copy the number

**Example:** `123456789`

Send your numeric ID now:
    """
    
    await message.answer(text, parse_mode="Markdown")


@router.message(BotCreationStates.waiting_for_admin_id)
async def process_admin_id(message: Message, state: FSMContext):
    """Process admin ID input."""
    admin_id = validate_admin_id(message.text)
    
    if not admin_id:
        await message.answer(
            "❌ Invalid admin ID. Please provide a valid numeric ID.\n\n"
            "Get your ID by messaging @userinfobot",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(admin_numeric_id=admin_id)
    await state.set_state(BotCreationStates.waiting_for_channel_id)
    
    text = """
📢 **Step 5: Channel Lock ID (Optional)**

If you want to restrict your bot to work only in a specific channel/group, provide the channel ID.

**How to get channel ID:**
1. Add your bot to the channel/group
2. Send a message in the channel
3. Forward that message to @userinfobot
4. It will show the channel ID (usually negative number)

**If you want your bot to work everywhere, just send "skip".**

Send your channel ID or "skip":
    """
    
    await message.answer(text, parse_mode="Markdown")


@router.message(BotCreationStates.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext):
    """Process channel ID input."""
    channel_id = validate_channel_id(message.text)
    
    if message.text.lower() in ["skip", "none", ""]:
        channel_id = None
    elif not channel_id:
        await message.answer(
            "❌ Invalid channel ID. Please provide a valid channel ID or send 'skip'.",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(channel_lock_id=channel_id)
    await state.set_state(BotCreationStates.confirming_creation)
    
    # Get subscription plans
    api_client = APIClient()
    try:
        plans = await api_client.get_subscription_plans()
        
        text = """
✅ **Bot Configuration Complete!**

**Your bot details:**
• Bot Token: `{}`
• GitHub Repo: `{}`
• Admin ID: `{}`
• Channel Lock: `{}`

**Choose a subscription plan:**
        """.format(
            "***" + (await state.get_data())["bot_token"][-10:],  # Show only last 10 chars
            (await state.get_data())["github_repo"],
            (await state.get_data())["admin_numeric_id"],
            (await state.get_data())["channel_lock_id"] or "None"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard_buttons = []
        for plan in plans[:3]:  # Show first 3 plans
            button_text = f"📦 {plan['name']} - ${plan['price']}"
            callback_data = f"select_plan:{plan['id']}"
            keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        
        keyboard_buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_creation")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error("Failed to get subscription plans", error=str(e))
        await message.answer(
            "❌ Failed to load subscription plans. Please try again later.",
            parse_mode="Markdown"
        )
        await state.clear()


@router.callback_query(F.data.startswith("select_plan:"))
async def select_plan(callback: CallbackQuery, state: FSMContext):
    """Handle plan selection."""
    await callback.answer()
    
    plan_id = callback.data.split(":")[1]
    data = await state.get_data()
    
    try:
        api_client = APIClient()
        
        # Create bot instance
        bot_data = {
            "bot_name": f"Bot-{data['admin_numeric_id']}",
            "bot_token": data["bot_token"],
            "github_repo": data["github_repo"],
            "github_token": data.get("github_token"),
            "admin_numeric_id": data["admin_numeric_id"],
            "channel_lock_id": data.get("channel_lock_id")
        }
        
        bot_instance = await api_client.create_bot_instance(bot_data)
        
        # Create subscription
        subscription_data = {
            "bot_instance_id": bot_instance["id"],
            "plan_id": plan_id,
            "start_at": "2024-01-01T00:00:00Z",  # This should be current time
            "end_at": "2024-02-01T00:00:00Z"     # This should be calculated from plan
        }
        
        subscription = await api_client.create_subscription(subscription_data)
        
        # Create payment
        payment_data = {
            "subscription_id": subscription["id"],
            "amount": 9.99,  # This should come from plan
            "currency": "USD",
            "payment_method": "bank_transfer"
        }
        
        payment = await api_client.create_payment(payment_data)
        
        success_text = """
🎉 **Bot Created Successfully!**

Your bot is being deployed. You'll receive a notification when it's ready.

**Next Steps:**
1. Complete payment to activate your bot
2. Monitor deployment progress
3. Your bot will be available once payment is confirmed

**Payment Details:**
• Amount: $9.99
• Method: Bank Transfer
• Reference: {}

Use /mybots to check your bot status.
        """.format(payment.get("bank_reference", "N/A"))
        
        await callback.message.edit_text(success_text, parse_mode="Markdown")
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to create bot", error=str(e))
        await callback.message.edit_text(
            "❌ Failed to create bot. Please try again later.\n\nError: {}".format(str(e)),
            parse_mode="Markdown"
        )
        await state.clear()


@router.callback_query(F.data == "cancel_creation")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    """Cancel bot creation."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Bot creation cancelled.")