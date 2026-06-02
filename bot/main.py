import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

from bot.config import BOT_TOKEN, STATE_WAITING_KEY, STATE_WAITING_NAME
from bot.handlers import (
    start_handler,
    main_menu_handler,
    process_name,
    activate_key_handler,
    process_key_handler,
    subjects_handler,
    select_subject_handler,
    parts_handler,
    select_part_handler,
    testing_handler,
    answer_handler,
    select_test_handler,
    answer_callback_handler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка. Попробуйте позже или обратитесь к преподавателю."
        )

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation для регистрации (ФИО)
    registration_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            STATE_WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)]
        },
        fallbacks=[CommandHandler("start", start_handler)]
    )

    # Conversation для активации ключа
    activate_key_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔑 Активировать ключ$"), activate_key_handler)],
        states={
            STATE_WAITING_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_key_handler)]
        },
        fallbacks=[CommandHandler("start", start_handler)]
    )

    # Обработчики
    application.add_handler(registration_conv)
    application.add_handler(activate_key_conv)

    # Меню (ВЫШЕ чем answer_handler!)
    application.add_handler(MessageHandler(filters.Regex("^📚 Мои предметы$"), subjects_handler))
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Назад$"), main_menu_handler))
    application.add_handler(MessageHandler(filters.Regex("^🔑 Активировать ключ$"), activate_key_handler))

    # Выбор предмета
    application.add_handler(MessageHandler(filters.Regex("^📖 .*"), select_subject_handler))

    # Выбор части
    application.add_handler(MessageHandler(filters.Regex("^Часть .*"), select_part_handler))

    # Выбор теста
    application.add_handler(MessageHandler(filters.Regex("^📝 .*"), select_test_handler))

    # Inline-кнопки ответов (ВАЖНО: ДО обычного answer_handler!)
    application.add_handler(CallbackQueryHandler(answer_callback_handler, pattern=r"^answer\|"))

    # Текстовые ответы ТОЛЬКО для открытых вопросов (НЕ перехватывает кнопки меню!)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(📚|⬅️|🔑|📖|Часть|📝)"),
        answer_handler
    ))

    application.add_error_handler(error_handler)

    logger.info("🤖 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()