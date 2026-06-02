import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Инициализация Firebase
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(r"D:\Клеверденд_бот\serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Загрузка JSON Части A (чистый формат)
json_path = r"D:\ct_2023_english_partA_clean.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Удаляем старые тесты Части A
print("🗑️ Удаляем старые тесты Части A...")
old_tests = db.collection('tests').stream()
deleted = 0
for test in old_tests:
    if test.id.startswith('ct2023_english') and test.id.endswith('_A'):
        test.reference.delete()
        deleted += 1
        print(f"  Удалён: {test.id}")

print(f"✅ Удалено: {deleted}\n")

# Загружаем в правильном формате (как история)
for variant_name, variant_data in data["variants"].items():
    test_id = f"ct2023_english_{variant_name}_A"
    
    # Формируем questions как МАССИВ
    questions = []
    for i, q in enumerate(variant_data["questions"]):
        questions.append({
            "text": q["text"],  # <-- Только вопрос, без вариантов ответов!
            "correct_text": None,
            "index": i,
            "type": "choice",
            "image_url": None,
            "part": "A",
            "correct_option": q["correct"],  # Индекс правильного ответа
            "options": q["options"]  # <-- Варианты только здесь (для кнопок)
        })
    
    # Создаём документ в ТОЧНОМ формате истории
    test_data = {
        "created_at": datetime.now(),
        "id": test_id,
        "subject_id": "english",
        "part": "A",
        "title": f"ЦТ/ЦЭ 2023 — {variant_name.replace('variant', 'Вариант')}",
        "is_active": True,
        "questions": questions,
        "teacher_id": "admin_001"
    }
    
    db.collection('tests').document(test_id).set(test_data)
    print(f"✅ {variant_name}: {test_id} ({len(questions)} вопросов)")

print(f"\n🎉 Готово! Загружено {len(data['variants'])} вариантов Части A!")
print("📌 Теперь варианты ответов только на кнопках, а не в тексте вопроса!")