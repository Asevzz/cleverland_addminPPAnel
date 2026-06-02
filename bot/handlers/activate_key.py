import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.services.firebase_service import FirebaseService
from bot.config import STATE_WAITING_KEY, SUBJECTS

async def show_activate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать запрос на ввод ключа"""
    await update.message.reply_text(
        "🔑 Введите ключ активации в формате: XXXX-XXXX-XXXX-XXXX\n\n"
        "Или нажмите ⬅️ Назад для возврата в меню.",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
    )
    return STATE_WAITING_KEY

async def process_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработать введённый ключ"""
    text = update.message.text.strip()
    tg_id = update.effective_user.id

    if text == "⬅️ Назад":
        from .start import start_handler
        await start_handler(update, context)
        return ConversationHandler.END

    # Проверяем формат ключа
    if len(text.replace('-', '')) != 16:
        await update.message.reply_text(
            "❌ Неверный формат ключа!\n"
            "Ключ должен содержать 16 символов (XXXX-XXXX-XXXX-XXXX).\n"
            "Попробуйте ещё раз:"
        )
        return STATE_WAITING_KEY

    # Нормализуем ключ
    key_code = text.upper().replace('-', '')
    key_code = '-'.join([key_code[i:i+4] for i in range(0, 16, 4)])

    # Проверяем ключ
    key_data = FirebaseService.get_key(key_code)

    if not key_data:
        await update.message.reply_text(
            "❌ Ключ не найден!\n"
            "Проверьте правильность ввода и попробуйте снова:"
        )
        return STATE_WAITING_KEY

    if key_data.get('is_used'):
        await update.message.reply_text(
            "❌ Этот ключ уже использован!\n"
            "Обратитесь к преподавателю за новым ключом."
        )
        return ConversationHandler.END

    # Активируем ключ
    subject_id, error = FirebaseService.activate_key(key_code, tg_id)

    if error:
        await update.message.reply_text(f"❌ Ошибка: {error}")
        return ConversationHandler.END

    subject_name = SUBJECTS.get(subject_id, {}).get('name', subject_id)

    await update.message.reply_text(
        f"✅ Ключ успешно активирован!\n\n"
        f"📚 Вам открыт доступ к предмету:\n"
        f"<b>{subject_name}</b>\n\n"
        f"Теперь вы можете проходить тесты по этому предмету!",
        parse_mode='HTML'
    )

    # Возвращаем в главное меню
    from .start import start_handler
    await start_handler(update, context)

    return ConversationHandler.END

from telegram import ReplyKeyboardMarkup
