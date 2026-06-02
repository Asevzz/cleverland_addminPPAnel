# 🤖 CleverLand Bot + Admin Panel

Проект для подготовки к ЦТ и ЦЭ: Telegram-бот для учеников и веб-панель для преподавателей.

## 📁 Структура проекта

```
cleverland/
├── bot/                    # Telegram-бот
│   ├── main.py            # Точка входа
│   ├── config.py          # Конфигурация
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   └── services/          # Сервисы (Firebase)
├── web/                    # Веб-панель
│   ├── app.py             # Flask приложение
│   ├── config.py          # Конфигурация
│   ├── auth.py            # Авторизация
│   ├── routes/            # Маршруты
│   ├── templates/         # HTML шаблоны
│   └── static/            # CSS/JS
├── shared/                 # Общие модули
│   └── firebase_config.py # Конфигурация Firebase
└── serviceAccountKey.json  # Ключи Firebase
```

## 🚀 Установка

### 1. Клонирование и настройка окружения

```bash
git clone <repo-url>
cd cleverland
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
# Для бота
pip install -r bot/requirements.txt

# Для веб-панели
pip install -r web/requirements.txt
```

### 3. Настройка Firebase

Файл `serviceAccountKey.json` уже настроен. Убедитесь, что в Firebase созданы коллекции:
- `subjects` — предметы
- `teachers` — преподаватели
- `tests` — тесты
- `activation_keys` — ключи активации
- `students` — ученики
- `answers` — ответы

### 4. Инициализация администратора

```bash
# Запустите веб-панель
python web/app.py

# Перейдите по адресу:
# http://localhost:5000/init-admin
```

Логин: `admin`  
Пароль: `cleverland_admin_2026`

### 5. Запуск

```bash
# Бот
python bot/main.py

# Веб-панель (в другом терминале)
python web/app.py
```

## 📱 Использование бота

1. Найдите бота `@cleverland_bot` в Telegram
2. Отправьте `/start`
3. Нажмите **🔑 Активировать ключ**
4. Введите ключ (формат: `XXXX-XXXX-XXXX-XXXX`)
5. Выберите предмет и часть
6. Проходите тесты!

## 🎨 Веб-панель

- **URL:** http://localhost:5000
- **Дизайн:** Сиренево-фиолетовая тема
- **Меню:** Справа
- **Функции:**
  - Создание/редактирование тестов
  - Управление ключами активации
  - Просмотр результатов учеников
  - Отвязка ключей

## 🔑 Формат ключей

```
XXXX-XXXX-XXXX-XXXX
(16 символов, группы по 4)

Пример: A7B2-C9D4-E1F6-G3H8
```

## 📊 Предметы

| Предмет | Тип | Части |
|---------|-----|-------|
| История Беларуси | ЦТ | А, Б, В |
| Английский | ЦЭ | A, B, C |
| Обществоведение | ЦТ | А, Б, В |

## 🛡️ Безопасность

- Ключи привязаны к Telegram ID
- Преподаватели видят только свои предметы
- Нет регистрации на сайте (только через админа)
- Пароли хешированы (bcrypt)

## 📞 Поддержка

По вопросам обращайтесь к администратору.
