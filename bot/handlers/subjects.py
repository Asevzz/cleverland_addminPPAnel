import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from telegram import Update
from telegram.ext import ContextTypes
from bot.services.firebase_service import FirebaseService
from bot.keyboards import get_subjects_keyboard, get_main_menu_keyboard
from bot.config import SUBJECTS

async def show_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список предметов ученика"""
    tg_id = update.effective_user.id
    student = FirebaseService.get_student(tg_id)

    if not student or not student.get('subjects'):
        await update.message.reply_text(
            "❌ У вас пока нет активированных предметов.\n"
            "Активируйте ключ, чтобы получить доступ!",
            reply_markup=get_main_menu_keyboard(False)
        )
        return

    subjects = student.get('subjects', {})

    await update.message.reply_text(
        "📚 Выберите предмет:",
        reply_markup=get_subjects_keyboard(list(subjects.keys()))
    )

async def select_subject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора предмета"""
    text = update.message.text

    if text == "⬅️ Назад":
        from .start import start_handler
        await start_handler(update, context)
        return

    # Извлекаем название предмета
    subject_name = text.replace("📖 ", "").strip()

    # Находим ID предмета
    subject_id = None
    for sid, sdata in SUBJECTS.items():
        if sdata['name'] == subject_name:
            subject_id = sid
            break

    if not subject_id:
        await update.message.reply_text("❌ Предмет не найден.")
        return

    # Сохраняем выбранный предмет в контексте
    context.user_data['selected_subject'] = subject_id

    # Показываем части
    from .parts import show_parts
    await show_parts(update, context, subject_id)
