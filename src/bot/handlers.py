import json
import urllib

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      Update, WebAppInfo, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext

from src.bot.constants import commands, states, callback_data
from src.bot.keyboards import get_categories_keyboard, get_subcategories_keyboard, MENU_KEYBOARD
from src.core.services.user import UserService
from src.settings import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    await user_service.register_user(
        telegram_id=update.effective_chat.id,
        username=update.effective_chat.username,
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Начнём",
                    callback_data=commands.GREETING,
                )
            ]
        ]
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! 👋 \n\n"
        'Я бот платформы интеллектуального волонтерства <a href="https://procharity.ru/">ProCharity</a>. '
        "Буду держать тебя в курсе новых задач и помогу "
        "оперативно связаться с командой поддержки.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def menu_callback(update: Update, context: CallbackContext):
    """Create button menu."""
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, что тебя интересует:", reply_markup=reply_markup)


async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = await get_categories_keyboard()
    await update.message.reply_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=reply_markup,
    )


async def subcategories_callback(update: Update, context: CallbackContext):
    parent_id = int(update.callback_query.data.split("_")[1])
    reply_markup = await get_subcategories_keyboard(parent_id)
    await update.callback_query.message.edit_text("Выберите категории", reply_markup=reply_markup)


async def ask_your_question(update: Update, context: CallbackContext):
    query = None
    text = "Задать вопрос"
    if update.effective_message.web_app_data:
        query = urllib.parse.urlencode(json.loads(update.effective_message.web_app_data.data))
        text = "Исправить неверно внесенные данные"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите на кнопку ниже, чтобы задать вопрос.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.feedback_form_template_url}"),
            )
        ),
    )


async def web_app_data(update: Update, context: CallbackContext):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [InlineKeyboardButton(text="Открыть в меню", callback_data="menu")],
        [InlineKeyboardButton(text="Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        text=f"Спасибо, я передал информацию команде ProCharity!"
             f"Ответ придет на почту ", # {user_data.get['email']}
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        text=f"Вы можете вернуться в меню или посмотреть открытые "
             f"задания. Нажмите на нужную кнопку.",
        reply_markup=keyboard,
    )
