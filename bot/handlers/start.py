import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.services.firebase_service import FirebaseService
from bot.config import STATE_WAITING_NAME

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    tg_id = update.effective_user.id
    username = update.effective_user.username
    
    student = FirebaseService.get_student(tg_id)

    if not student:
        await update.message.reply_text(
            "👋 Добро пожаловать в CleverLand!\n\n"
            "Для начала работы введите ваше ФИО (фамилию и имя):\n"
            "Например: Иванов Иван",
            reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)
        )
        return STATE_WAITING_NAME

    await show_main_menu(update, context, student)
    return ConversationHandler.END

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода ФИО"""
    text = update.message.text.strip()
    tg_id = update.effective_user.id
    username = update.effective_user.username

    if text == "❌ Отмена":
        await update.message.reply_text("Регистрация отменена. Нажмите /start для повтора.")
        return ConversationHandler.END

    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Неверный формат! Введите фамилию и имя через пробел:\n"
            "Например: Иванов Иван"
        )
        return STATE_WAITING_NAME

    last_name = parts[0]
    first_name = ' '.join(parts[1:])

    FirebaseService.create_student(tg_id, username, first_name, last_name)
    student = FirebaseService.get_student(tg_id)

    await update.message.reply_text(
        f"✅ Регистрация завершена!\n\n"
        f"👤 {last_name} {first_name}\n\n"
        f"Теперь активируйте ключ, чтобы получить доступ к предметам!"
    )

    await show_main_menu(update, context, student)
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, student=None):
    """Показать главное меню"""
    if not student:
        tg_id = update.effective_user.id
        student = FirebaseService.get_student(tg_id)

    subjects = student.get('subjects', {}) if student else {}
    has_subjects = len(subjects) > 0
    first_name = student.get('first_name', 'Ученик') if student else 'Ученик'

    welcome_text = f"👋 Привет, {first_name}!\n\n"
    welcome_text += "🤖 CleverLand — бот для подготовки к ЦТ и ЦЭ!\n\n"

    if has_subjects:
        welcome_text += "📚 Ваши предметы:\n"
        from bot.config import SUBJECTS
        for subject_id in subjects:
            subject_name = SUBJECTS.get(subject_id, {}).get('name', subject_id)
            welcome_text += f"  • {subject_name}\n"
        welcome_text += "\nВыберите действие:"
    else:
        welcome_text += "🔑 У вас пока нет доступных предметов.\n"
        welcome_text += "Активируйте ключ, чтобы начать обучение!"

    from bot.keyboards import get_main_menu_keyboard
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(has_subjects)
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    text = update.message.text
    tg_id = update.effective_user.id
    student = FirebaseService.get_student(tg_id)

    if text == "📚 Мои предметы":
        from .subjects import show_subjects
        await show_subjects(update, context)
    elif text == "🔑 Активировать ключ":
        from .activate_key import show_activate_key
        await show_activate_key(update, context)
    elif text == "⬅️ Назад":
        await show_main_menu(update, context, student)