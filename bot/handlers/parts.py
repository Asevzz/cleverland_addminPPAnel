import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import get_parts_keyboard
from bot.config import SUBJECTS

async def show_parts(update: Update, context: ContextTypes.DEFAULT_TYPE, subject_id):
    """Показать части предмета"""
    subject = SUBJECTS.get(subject_id, {})
    subject_name = subject.get('name', subject_id)

    await update.message.reply_text(
        f"📖 <b>{subject_name}</b>\n\n"
        f"Выберите часть для прохождения тестов:",
        parse_mode='HTML',
        reply_markup=get_parts_keyboard(subject_id)
    )

async def select_part_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора части"""
    text = update.message.text

    if text == "⬅️ Назад":
        from .subjects import show_subjects
        await show_subjects(update, context)
        return

    if not text.startswith("Часть "):
        return

    part = text.replace("Часть ", "").strip()
    subject_id = context.user_data.get('selected_subject')

    if not subject_id:
        await update.message.reply_text("❌ Ошибка: предмет не выбран.")
        return

    # Сохраняем часть в контексте
    context.user_data['selected_part'] = part

    # Показываем список тестов
    from .testing import show_tests
    await show_tests(update, context, subject_id, part)
