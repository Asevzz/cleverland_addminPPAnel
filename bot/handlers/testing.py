import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.services.firebase_service import FirebaseService
from bot.keyboards import get_question_inline_keyboard
from bot.config import SUBJECTS
import asyncio

async def show_tests(update: Update, context: ContextTypes.DEFAULT_TYPE, subject_id, part):
    """Показать список тестов"""
    tests = FirebaseService.get_tests_by_subject_and_part(subject_id, part)

    if not tests:
        subject_name = SUBJECTS.get(subject_id, {}).get('name', subject_id)
        await update.message.reply_text(
            f"📖 <b>{subject_name} — Часть {part}</b>\n\n"
            f"😕 Пока нет доступных тестов по этой части.\n"
            f"Обратитесь к преподавателю.",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
        )
        return

    subject_name = SUBJECTS.get(subject_id, {}).get('name', subject_id)
    text = f"📖 <b>{subject_name} — Часть {part}</b>\n\n"
    text += "Выберите тест:\n\n"

    keyboard = []
    for i, test in enumerate(tests):
        text += f"{i+1}. {test.get('title', 'Без названия')}\n"
        keyboard.append([f"📝 {test.get('title', 'Тест ' + str(i+1))}"])

    keyboard.append(["⬅️ Назад"])

    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    context.user_data['available_tests'] = tests

async def select_test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора конкретного теста"""
    text = update.message.text

    if text == "⬅️ Назад":
        from .parts import show_parts
        subject_id = context.user_data.get('selected_subject')
        await show_parts(update, context, subject_id)
        return

    if not text.startswith("📝 "):
        return

    test_title = text.replace("📝 ", "").strip()
    tests = context.user_data.get('available_tests', [])

    selected_test = None
    for test in tests:
        if test.get('title') == test_title:
            selected_test = test
            break

    if not selected_test:
        await update.message.reply_text("❌ Тест не найден.")
        return

    test_id = selected_test.get('id')
    tg_id = update.effective_user.id

    FirebaseService.clear_answers(tg_id, test_id)

    context.user_data['current_test'] = selected_test
    context.user_data['current_question'] = 0
    context.user_data['test_id'] = test_id
    context.user_data.pop('available_tests', None)

    await show_question(update, context)

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать текущий вопрос — варианты только в кнопках"""
    test = context.user_data.get('current_test')
    question_index = context.user_data.get('current_question', 0)
    questions = test.get('questions', [])

    if question_index >= len(questions):
        await finish_test(update, context)
        return

    question = questions[question_index]
    q_type = question.get('type', 'choice')
    image_url = question.get('image_url')

    # Только вопрос, без вариантов
    text = f"❓ <b>Вопрос {question_index + 1} из {len(questions)}</b>\n\n"
    text += f"{question.get('text', '')}"

    # Определяем, откуда отправлять
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    if image_url:
        try:
            await message.reply_photo(
                photo=image_url,
                caption=text,
                parse_mode='HTML'
            )
            text = "Выберите ответ:"
        except Exception as e:
            print(f"Ошибка загрузки картинки: {e}")

    if q_type == 'choice':
        options = question.get('options', [])
        
        # Варианты только в кнопках, не в тексте!
        keyboard = get_question_inline_keyboard(options, question_index)

        await message.reply_text(
            text,  # Только вопрос, без вариантов
            parse_mode='HTML',
            reply_markup=keyboard
        )
    else:
        text += "\n\n✏️ Напишите ваш ответ одним словом:"
        await message.reply_text(text, parse_mode='HTML')

    context.user_data['waiting_answer'] = True
    
async def answer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline-кнопок с ответами"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('|')
    if data[0] != 'answer':
        return
    
    question_index = int(data[1])
    answer_num = int(data[2])
    
    tg_id = update.effective_user.id
    test = context.user_data.get('current_test')
    
    if not test:
        await query.edit_message_text("❌ Тест не найден. Начните заново.")
        return
    
    questions = test.get('questions', [])
    if question_index >= len(questions):
        await finish_test(update, context)
        return
    
    question = questions[question_index]
    
    correct_option = question.get('correct_option', 0)
    is_correct = (answer_num == correct_option)
    given_answer = question.get('options', [])[answer_num]
    
    FirebaseService.save_answer(
        tg_id,
        test.get('id'),
        question_index,
        given_answer,
        is_correct,
        question.get('part', '')
    )
    
    if is_correct:
        result_text = f"✅ Ваш ответ верный - {given_answer} ({question_index + 1})"
    else:
        correct_answer = question.get('options', [])[correct_option]
        result_text = f"❌ Ваш ответ неверный. Правильный ответ: {correct_answer} ({correct_option + 1})"
    
    await query.edit_message_text(
        f"{query.message.text}\n\n{result_text}",
        parse_mode='HTML'
    )
    
    context.user_data['current_question'] = question_index + 1
    context.user_data['waiting_answer'] = False
    
    await asyncio.sleep(1)
    await show_question(update, context)

async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых ответов (только для открытых вопросов)"""
    if not context.user_data.get('waiting_answer'):
        return

    text = update.message.text.strip()
    tg_id = update.effective_user.id

    test = context.user_data.get('current_test')
    question_index = context.user_data.get('current_question', 0)
    questions = test.get('questions', [])
    question = questions[question_index]

    q_type = question.get('type', 'choice')
    
    if q_type == 'choice':
        return

    is_correct = False
    given_answer = text

    correct_text = question.get('correct_text', '').lower().strip()
    is_correct = (text.lower().strip() == correct_text)

    FirebaseService.save_answer(
        tg_id,
        test.get('id'),
        question_index,
        given_answer,
        is_correct,
        question.get('part', '')
    )

    if is_correct:
        result_text = f"✅ Ваш ответ верный - {given_answer} ({question_index + 1})"
    else:
        correct_text = question.get('correct_text', '')
        result_text = f"❌ Ваш ответ неверный. Правильный ответ: {correct_text}"

    await update.message.reply_text(result_text, parse_mode='HTML')

    context.user_data['current_question'] = question_index + 1
    context.user_data['waiting_answer'] = False

    await show_question(update, context)

async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение теста"""
    test = context.user_data.get('current_test')
    tg_id = update.effective_user.id
    test_id = test.get('id')

    questions = test.get('questions', [])
    total = len(questions)
    
    answers = FirebaseService.get_student_answers(tg_id, test_id)
    
    recent_answers = answers[-total:] if len(answers) >= total else answers
    correct_count = sum(1 for a in recent_answers if a.get('is_correct'))

    # Определяем, откуда отправлять
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text(
        f"🎉 <b>Тест завершён!</b>\n\n"
        f"📊 Результат:\n"
        f"✅ Правильных: {correct_count} из {total}\n"
        f"📈 Процент: {round(correct_count/total*100) if total > 0 else 0}%\n\n"
        f"Можете выбрать другой тест!",
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup([["📚 Мои предметы"], ["⬅️ Назад"]], resize_keyboard=True)
    )

    context.user_data.pop('current_test', None)
    context.user_data.pop('current_question', None)
    context.user_data.pop('test_id', None)
    context.user_data.pop('waiting_answer', None)
    context.user_data.pop('available_tests', None)
    context.user_data.pop('selected_part', None)