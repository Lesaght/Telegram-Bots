# Telegram Meme Bot 🎬

Асинхронный Telegram-бот на Python для управления мемами с модерацией перед публикацией.

## 📋 Содержание

- [Функционал](#функционал)
- [Требования](#требования)
- [Установка](#установка)
- [Настройка](#настройка)
- [Запуск](#запуск)
- [Использование](#использование)
- [Структура проекта](#структура-проекта)
- [Безопасность](#безопасность)

## ✨ Функционал

### Для пользователей:
- `/start` - Регистрация и приветствие
- `/upload` - Загрузка мема на модерацию (фото или видео)
- `/meme` - Просмотр случайного одобренного мема
- Оценка мемов (👍/👎)
- Автоматический переход к следующему мему

### Для модераторов:
- Получение уведомлений о новых мемах в специальном чате
- Одобрение или отклонение мемов через inline-кнопки
- Отслеживание статуса модерации

## 🔧 Требования

- **Python 3.11+**
- **pip** (менеджер пакетов Python)
- **Git** (для клонирования репозитория)
- **Telegram аккаунт** с доступом к BotFather
- **Supabase аккаунт** (бесплатная база данных PostgreSQL)

## 📥 Установка

### Шаг 1: Клонируйте репозиторий

```bash
# Используя Git
git clone https://github.com/Lesaght/uuu.git
cd Meme-bot
```

Или скачайте ZIP архив прямо с GitHub и распакуйте его.

### Шаг 2: Проверьте версию Python

```bash
python --version
# или
python3 --version
```

Должна быть версия **3.11 или выше**.

### Шаг 3: Установите виртуальное окружение (рекомендуется)

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# На Linux/macOS:
source venv/bin/activate

# На Windows:
venv\Scripts\activate
```

### Шаг 4: Установите зависимости

```bash
pip install -r requirements.txt
```

## ⚙️ Настройка

### 1. Создайте файл `.env`

В корневой папке проекта создайте файл `.env`:

```bash
# Linux/macOS
touch .env

# Windows
echo. > .env
```

### 2. Получите Telegram Bot Token

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите название для бота (например: "MyMemeBot")
   - Введите username для бота (должен заканчиваться на `_bot`, например: `my_meme_bot`)
4. BotFather выдаст вам токен вида: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### 3. Получите Moderation Chat ID

1. Создайте приватный канал или группу в Telegram для модерации
2. Добавьте туда своего бота как администратора
3. Используйте [@userinfobot](https://t.me/userinfobot):
   - Откройте бота
   - Нажмите `/start`
   - Перейдите в ваш модерационный чат/канал
   - Используйте команду `/getgroupid` (если доступна) или просто откройте группу и бот покажет ID
4. ID должен начинаться с `-100` (например: `-1001234567890`)

### 4. Получите Supabase учетные данные

1. Перейдите на [supabase.com](https://supabase.com)
2. Нажмите "Sign Up" и создайте аккаунт
3. Создайте новый проект
4. В левом меню откройте **Settings → API**
5. Скопируйте:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY`

### 5. Заполните файл `.env`

```env
# Telegram Bot Token (получили от BotFather)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# ID модерационного чата/канала
MODERATION_CHAT_ID=-1001234567890

# Supabase (проект автоматически создает таблицы при первом запуске)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 6. Настройте базу данных

База данных настраивается автоматически при первом запуске, но если нужно вручную, выполните в Supabase SQL редакторе:

```sql
-- Эти таблицы создадутся автоматически при первом запуске бота
-- Но вы можете создать их вручную, если нужно
```

### 7. Назначьте модераторов

После первого запуска бота:

1. Откройте [Supabase Dashboard](https://app.supabase.com)
2. Перейдите в **SQL Editor**
3. Выполните запрос:

```sql
UPDATE users SET is_moderator = true WHERE id = YOUR_TELEGRAM_USER_ID;
```

4. Узнайте свой Telegram ID через [@userinfobot](https://t.me/userinfobot)

## 🚀 Запуск

### Вариант 1: Запуск в терминале

```bash
python main.py
```

Вы должны увидеть сообщение: `Bot started polling...`

### Вариант 2: Запуск на фоне (Linux/macOS)

```bash
nohup python main.py > bot.log 2>&1 &
```

### Вариант 3: Запуск с использованием screen

```bash
screen -S meme_bot python main.py
# Для выхода: Ctrl+A, затем D
# Для возврата: screen -r meme_bot
```

### Вариант 4: Запуск на сервере (systemd)

Создайте файл `/etc/systemd/system/meme-bot.service`:

```ini
[Unit]
Description=Telegram Meme Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/uuu
ExecStart=/path/to/uuu/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl enable meme-bot
sudo systemctl start meme-bot
sudo systemctl status meme-bot
```

## 📱 Использование

### Для пользователей:

1. Найдите бота в Telegram по его username
2. Нажмите `/start` для регистрации
3. Используйте `/upload` для загрузки мема
4. Используйте `/meme` для просмотра одобренных мемов
5. Оценивайте мемы кнопками 👍 или 👎

### Для модераторов:

1. Новые мемы автоматически появляются в модерационном чате
2. Нажмите ✅ для одобрения или ❌ для отклонения
3. Только одобренные мемы появляются в `/meme`

## 📁 Структура проекта

```
uuu/
├── main.py                       # Точка входа приложения
├── config.py                     # Конфигурация и настройки
├── keyboards.py                  # Inline-клавиатуры для бота
├── database/
│   ├── __init__.py
│   ├── client.py                # Supabase клиент
│   └── crud.py                  # CRUD операции с БД
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py         # Обработчики пользовательских команд
│   └── moderator_handlers.py    # Обработчики модерации
├── requirements.txt              # Зависимости Python
├── .env                          # Переменные окружения (игнорируется Git)
├── .gitignore                    # Файлы, игнорируемые Git
└── README.md                     # Эта документация
```

## 🔐 Безопасность

- ✅ Row Level Security (RLS) настроен для всех таблиц
- ✅ Только модераторы могут одобрять/отклонять мемы
- ✅ Заблокированные пользователи не могут загружать мемы
- ✅ Один пользователь может дать только одну оценку одному мему
- ✅ Токены хранятся в `.env` (НЕ коммитьте этот файл!)

## 🗄️ Структура базы данных

### Таблица `users`
- `id` (bigint) - Telegram ID пользователя
- `username` (text) - Username пользователя
- `is_moderator` (boolean) - Флаг модератора
- `is_banned` (boolean) - Статус блокировки

### Таблица `memes`
- `id` (serial) - ID мема
- `file_id` (text) - ID файла в Telegram
- `user_id` (bigint) - ID пользователя-загрузчика
- `status` (text) - Статус: PENDING, APPROVED, REJECTED
- `uploaded_at` (timestamptz) - Время загрузки
- `moderated_at` (timestamptz) - Время модерации
- `moderated_by` (bigint) - ID модератора

### Таблица `ratings`
- `id` (serial) - ID оценки
- `meme_id` (integer) - ID мема
- `user_id` (bigint) - ID пользователя
- `value` (integer) - Значение оценки (+1 или -1)
- Уникальный индекс по (meme_id, user_id)

## 🐛 Решение проблем

### Проблема: `ModuleNotFoundError: No module named 'aiogram'`
**Решение:** Установите зависимости: `pip install -r requirements.txt`

### Проблема: `Invalid token` при запуске
**Решение:** Проверьте правильность `TELEGRAM_BOT_TOKEN` в файле `.env`

### Проблема: Бот не подключается к базе данных
**Решение:** Проверьте `SUPABASE_URL` и `SUPABASE_KEY` в `.env`

### Проблема: Мемы не отправляются в модерационный чат
**Решение:** Убедитесь, что бот добавлен как администратор в модерационный чат и `MODERATION_CHAT_ID` верен

## 📚 Технический стек

- **Python 3.11+** - Язык программирования
- **aiogram 3.x** - Асинхронная библиотека для Telegram Bot API
- **Supabase** - База данных PostgreSQL в облаке
- **pydantic-settings** - Управление конфигурацией

## 🚀 Возможные улучшения

- 🔲 Добавить админ-панель для управления модераторами
- ���� Реализовать статистику по мемам
- 🔲 Добавить категории для мемов
- 🔲 Реализовать систему жалоб
- 🔲 Добавить топ-рейтинг мемов
- 🔲 Реализовать отложенную публикацию

## 📝 Лицензия

Этот проект открыт для использования и модификации.

## ❓ Вопросы и поддержка

Если у вас возникли проблемы, проверьте:
1. Правильность всех ключей в `.env`
2. Что Python версия 3.11+
3. Что виртуальное окружение активировано
4. Логи бота на предмет ошибок
