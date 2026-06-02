import json
import firebase_admin
from firebase_admin import credentials, firestore
import os
import traceback

# Инициализация Firebase
try:
    firebase_admin.get_app()
except ValueError:
    try:
        cred = credentials.Certificate(r"D:\Клеверденд_бот\serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"❌ Ошибка инициализации Firebase: {e}")
        exit(1)

db = firestore.client()

def export_collection(collection_path, depth=0, max_depth=4):
    """Рекурсивный экспорт коллекции с подколлекциями"""
    if depth > max_depth:
        return "...(max depth reached)"
    
    try:
        docs = list(db.collection(collection_path).stream())
        if not docs:
            return {}
        
        result = {}
        for doc in docs:
            try:
                data = doc.to_dict() or {}
                
                # Конвертируем datetime в строку
                for key, value in list(data.items()):
                    if hasattr(value, 'isoformat'):
                        data[key] = value.isoformat()
                    elif isinstance(value, dict):
                        # Рекурсивно конвертируем вложенные datetime
                        for k, v in list(value.items()):
                            if hasattr(v, 'isoformat'):
                                value[k] = v.isoformat()
                
                # Ищем подколлекции
                try:
                    subcollections = list(doc.reference.collections())
                    for subcol in subcollections:
                        subcol_name = subcol.id
                        subcol_path = f"{collection_path}/{doc.id}/{subcol_name}"
                        data[f"__subcollection_{subcol_name}"] = export_collection(subcol_path, depth + 1, max_depth)
                except Exception as e:
                    data[f"__subcollection_error"] = str(e)
                
                result[doc.id] = data
                
            except Exception as e:
                result[doc.id] = {"__error": str(e)}
        
        return result
        
    except Exception as e:
        return {"__error": str(e)}

def get_all_collections():
    """Получает список всех корневых коллекций"""
    try:
        # Получаем все корневые коллекции
        collections = db.collections()
        return [col.id for col in collections]
    except Exception as e:
        print(f"❌ Ошибка получения коллекций: {e}")
        return []

# === ОСНОВНОЙ ЭКСПОРТ ===
try:
    print("🔍 Получаем список коллекций...")
    all_collections = get_all_collections()
    print(f"📁 Найдено коллекций: {all_collections}")
    
    full_database = {}
    
    for collection_name in all_collections:
        print(f"\n⏳ Экспортируем '{collection_name}'...")
        full_database[collection_name] = export_collection(collection_name)
        print(f"✅ '{collection_name}' экспортирована")
    
    # Сохраняем в JSON
    output_path = r"D:\Клеверденд_бот\full_database_export.json"
    
    print(f"\n💾 Сохраняем в: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_database, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 УСПЕХ! Файл сохранён: {output_path}")
    print(f"📊 Размер: {os.path.getsize(output_path)} байт")
    print(f"📂 Коллекций: {len(full_database)}")
    
    # Выводим структуру
    print(f"\n📋 Структура базы:")
    for col_name, col_data in full_database.items():
        doc_count = len(col_data) if isinstance(col_data, dict) else 0
        print(f"  ├── {col_name} ({doc_count} документов)")

except Exception as e:
    print(f"\n❌ Критическая ошибка: {e}")
    traceback.print_exc()
    
    # Пробуем сохранить то, что успели собрать
    try:
        if 'full_database' in locals():
            emergency_path = r"D:\Клеверденд_бот\database_partial.json"
            with open(emergency_path, 'w', encoding='utf-8') as f:
                json.dump(full_database, f, ensure_ascii=False, indent=2)
            print(f"⚠️ Частичный экспорт сохранён: {emergency_path}")
    except:
        pass