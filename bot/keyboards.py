from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard(has_subjects=False):
    """Главное меню"""
    keyboard = []
    if has_subjects:
        keyboard.append(["📚 Мои предметы"])
    keyboard.append(["🔑 Активировать ключ"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_subjects_keyboard(subject_ids):
    """Клавиатура предметов"""
    from bot.config import SUBJECTS
    keyboard = []
    for sid in subject_ids:
        name = SUBJECTS.get(sid, {}).get('name', sid)
        keyboard.append([f"📖 {name}"])
    keyboard.append(["⬅️ Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_parts_keyboard(subject_id):
    """Клавиатура частей предмета"""
    from bot.config import SUBJECTS
    subject = SUBJECTS.get(subject_id, {})
    parts = subject.get('parts', ['А', 'Б', 'В'])
    
    keyboard = []
    for part in parts:
        keyboard.append([f"Часть {part}"])
    keyboard.append(["⬅️ Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_question_inline_keyboard(options, question_index):
    """Inline-кнопки для вариантов ответа"""
    keyboard = []
    row = []
    
    for i, option in enumerate(options):
        callback_data = f"answer|{question_index}|{i}"
        row.append(InlineKeyboardButton(f"{option} ({i+1})", callback_data=callback_data))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard(has_subjects=False):
    """Главное меню"""
    keyboard = []
    if has_subjects:
        keyboard.append(["📚 Мои предметы"])
    keyboard.append(["🔑 Активировать ключ"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_subjects_keyboard(subject_ids):
    """Клавиатура предметов"""
    from bot.config import SUBJECTS
    keyboard = []
    for sid in subject_ids:
        name = SUBJECTS.get(sid, {}).get('name', sid)
        keyboard.append([f"📖 {name}"])
    keyboard.append(["⬅️ Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_parts_keyboard(subject_id):
    """Клавиатура частей предмета"""
    from bot.config import SUBJECTS
    subject = SUBJECTS.get(subject_id, {})
    parts = subject.get('parts', ['А', 'Б', 'В'])
    
    keyboard = []
    for part in parts:
        keyboard.append([f"Часть {part}"])
    keyboard.append(["⬅️ Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_question_inline_keyboard(options, question_index):
    """Inline-кнопки для вариантов ответа"""
    keyboard = []
    row = []
    
    for i, option in enumerate(options):
        callback_data = f"answer|{question_index}|{i}"
        row.append(InlineKeyboardButton(f"{option} ({i+1})", callback_data=callback_data))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)