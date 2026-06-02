from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard(has_subjects=False):
    """Главное меню"""
    buttons = []
    if has_subjects:
        buttons.append([KeyboardButton("📚 Мои предметы")])
    buttons.append([KeyboardButton("🔑 Активировать ключ")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_subjects_keyboard(subjects):
    """Клавиатура выбора предметов"""
    from bot.config import SUBJECTS
    buttons = []
    for subject_id in subjects:
        subject_name = SUBJECTS.get(subject_id, {}).get('name', subject_id)
        buttons.append([KeyboardButton(f"📖 {subject_name}")])
    buttons.append([KeyboardButton("⬅️ Назад")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_parts_keyboard(subject_id):
    """Клавиатура выбора частей"""
    from bot.config import SUBJECTS
    subject = SUBJECTS.get(subject_id, {})
    parts = subject.get('parts', [])
    buttons = []
    for part in parts:
        buttons.append([KeyboardButton(f"Часть {part}")])
    buttons.append([KeyboardButton("⬅️ Назад")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_answer_keyboard(options, question_type="choice"):
    """Клавиатура ответов (для текстовых вопросов)"""
    if question_type == "text":
        return None
    buttons = []
    for i, option in enumerate(options):
        buttons.append([KeyboardButton(f"{i+1}. {option}")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

def get_question_inline_keyboard(options, question_index):
    """Inline-кнопки для вариантов ответа — по одной в ряд, красиво"""
    keyboard = []
    for i, option in enumerate(options):
        callback_data = f"answer|{question_index}|{i}"
        keyboard.append([
            InlineKeyboardButton(
                f"{i+1}. {option}",
                callback_data=callback_data
            )
        ])
    return InlineKeyboardMarkup(keyboard)