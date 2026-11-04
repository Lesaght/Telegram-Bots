# 🎮 Steam Bot for Telegram | Телеграм-бот для Steam

<div align="center">

[🇬🇧 English](#english-version) • [🇷🇺 Русский](#russian-version)

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.29.0-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

**A powerful Telegram bot for monitoring Steam profiles, inventory, and friends** ⚡

</div>

---

## English Version

### ✨ Features

<details open>
<summary><strong>👤 Profile Information</strong></summary>

- Search by username, profile URL, or SteamID64
- View avatar, status, country, account level
- Account creation date and last online time
- VAC bans and game bans information
- Comprehensive account statistics

</details>

<details>
<summary><strong>🎮 Games & Library</strong></summary>

- Complete game library sorted by playtime
- Random game picker
- Recently played games tracking
- Advanced sorting and filtering

</details>

<details>
<summary><strong>📊 CS2 Statistics</strong></summary>

- K/D ratio tracking
- Win percentage and rounds played
- Accuracy, headshot stats, MVP badges
- Detailed match history insights

</details>

<details>
<summary><strong>💰 Inventory Management</strong></summary>

- Steam market price evaluation for CS2, Dota 2, TF2
- Steam cards breakdown (foil, backgrounds, emotes, stickers, boosters)
- Item search within inventory
- Top 10 most expensive items
- Real-time market tracking

</details>

<details>
<summary><strong>⭐ Favorites System</strong></summary>

- Store up to 10 profiles
- Quick access from main menu
- Easy selection for comparisons

</details>

<details>
<summary><strong>🔔 Notifications (Background Monitoring)</strong></summary>

| Type | Trigger |
|------|---------|
| 🎮 Game Alert | Favorite player started/switched games |
| 🟢 Online Alert | Player came online (offline → online) |
| 📈 Price Tracker | Item price dropped below threshold |

</details>

<details>
<summary><strong>⚖️ Profile Comparison</strong></summary>

- Compare two players by level, games, hours, VAC status
- Find common games sorted by playtime
- List common friends
- Select from favorites or enter manually

</details>

<details>
<summary><strong>🏆 Friends Leaderboard</strong></summary>

- Rank friends by playtime in selected game
- Interactive selection and viewing

</details>

### 🏗 Architecture

```
botSteam/
├── main.py                  # Entry point, router registration
├── config.py                # Environment configuration
├── bot/
│   ├── handlers/
│   │   ├── start.py         # Main menu, help, favorites, alerts
│   │   ├── profile.py       # Player profile
│   │   ├── friends.py       # Friends list
│   │   ├── recent.py        # Recent games
│   │   ├── games.py         # Library & random game
│   │   ├── inventory.py     # Inventory & search
│   │   ├── cs2stats.py      # CS2 statistics
│   │   ├── compare.py       # Comparison, common games/friends
│   │   ├── leaderboard.py   # Friends top by game
│   │   ├── favorites.py     # Add/remove favorites
│   │   ├── online_alert.py  # Manage online alerts
│   │   └── price_tracker.py # Item price tracker
│   ├── keyboards/
│   │   └── inline.py        # All keyboards & CallbackData classes
│   └── states.py            # FSM states
├── services/
│   ├── steam.py             # Steam Web & Community API wrapper
│   ├── storage.py           # JSON storage (favorites, alerts)
│   └── notifier.py          # Background monitoring & notifications
├── utils/
│   └── formatters.py        # Profile & date formatting
└── data/                    # Auto-created on first run
    ├── favorites.json
    ├── online_alerts.json
    ├── price_alerts.json
    ├── last_seen.json
    └── last_online.json
```

### 🚀 Installation & Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Lesaght/botSteam.git
cd botSteam
```

#### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Configure `.env` File
```env
TELEGRAM_TOKEN=your_token_from_BotFather
STEAM_API_KEY=your_Steam_Web_API_key
```

- **Telegram Token**: Get from [@BotFather](https://t.me/BotFather)
- **Steam API Key**: Get from [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)

#### 4. Run Bot
```bash
python main.py
```

### 🛠 Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Programming language |
| aiogram | 3.29.0 | Telegram Bot Framework |
| aiohttp | 3.14.1 | Async HTTP requests to Steam API |
| aiofiles | 25.1.0 | Async file operations |
| python-dotenv | 1.2.2 | Environment variables |
| certifi | latest | SSL certificates (macOS fix) |

### 📡 APIs Used

**Steam Web API** (`api.steampowered.com`)
- `ISteamUser/GetPlayerSummaries` — profile data
- `ISteamUser/GetFriendList` — friends list
- `ISteamUser/GetPlayerBans` — VAC & game bans
- `ISteamUser/ResolveVanityURL` — nickname resolution
- `IPlayerService/GetOwnedGames` — game library
- `IPlayerService/GetRecentlyPlayedGames` — recent games
- `IPlayerService/GetSteamLevel` — Steam level
- `ISteamUserStats/GetUserStatsForGame` — CS2 stats

**Steam Community API**
- `steamcommunity.com/inventory/{steamid}/{appid}/{contextid}` — inventory
- `steamcommunity.com/market/priceoverview/` — market prices

### ⚙️ Technical Details

- **Concurrent Requests** — `asyncio.gather()` for parallel API calls
- **Rate Limiting** — `asyncio.Semaphore(5)` with 300ms delays
- **FSM** — aiogram finite state machines for user input
- **Background Monitoring** — `asyncio.create_task()` runs notifier in parallel
- **Storage** — JSON files with async I/O via aiofiles
- **macOS SSL Fix** — certifi CA bundle for Python certificates

### 📋 Limits

| Parameter | Value |
|-----------|-------|
| Max favorite profiles | 10 |
| Max price trackers | 20 |
| Top inventory items | 10 |
| Top library games | 15 |
| Friends in leaderboard | up to 100 |
| Notification check interval | 300 seconds |

---

## Russian Version

### ✨ Возможности

<details open>
<summary><strong>👤 Информация о профиле</strong></summary>

- Поиск по нику, ссылке профиля или SteamID64
- Просмотр аватара, статуса, страны, уровня аккаунта
- Дата создания аккаунта и время последнего выхода в сеть
- Информация о VAC-банах и игровых блокировках
- Полная статистика аккаунта

</details>

<details>
<summary><strong>🎮 Игры и библиотека</strong></summary>

- Полная библиотека с сортировкой по наигранным часам
- Случайная игра из библиотеки
- Список недавно запущенных игр
- Продвинутая фильтрация и сортировка

</details>

<details>
<summary><strong>📊 Статистика CS2</strong></summary>

- Убийства, смерти, K/D ratio
- Процент побед, сыгранные раунды
- Точность стрельбы, хедшоты, MVP
- Детальная статистика матчей

</details>

<details>
<summary><strong>💰 Управление инвентарем</strong></summary>

- Оценка стоимости инвентаря CS2, Dota 2, TF2 по рыночным ценам
- Карточки Steam — разбивка по типам: карточки, фольга, фоны профиля, смайлики, наклейки, бустеры
- Поиск предметов по названию внутри инвентаря
- Топ-10 самых дорогих предметов
- Отслеживание цен в реальном времени

</details>

<details>
<summary><strong>⭐ Система избранного</strong></summary>

- До 10 профилей в избранном
- Быстрый доступ из главного меню
- Легкий выбор для сравнения профилей

</details>

<details>
<summary><strong>🔔 Уведомления (фоновый мониторинг)</strong></summary>

| Тип | Триггер |
|-----|---------|
| 🎮 Игровое уведомление | Игрок из избранного начал/сменил игру |
| 🟢 Онлайн-алерт | Игрок появился в сети (был оффлайн → онлайн) |
| 📈 Трекер цен | Цена предмета на маркете упала до заданного порога |

</details>

<details>
<summary><strong>⚖️ Сравнение профилей</strong></summary>

- Сравнение двух игроков по уровню, количеству игр, часам, VAC-статусу
- Поиск общих игр с сортировкой по времени в игре
- Список общих друзей
- Выбор игроков из избранного или ввод вручную

</details>

<details>
<summary><strong>🏆 Топ друзей</strong></summary>

- Рейтинг друзей по наигранным часам в выбранной игре
- Интерактивное отображение и выбор

</details>

### 🏗 Архитектура проекта

```
botSteam/
├── main.py                  # Точка входа, регистрация роутеров
├── config.py                # Конфигурация окружения
├── bot/
│   ├── handlers/
│   │   ├── start.py         # Главное меню, помощь, избранное, алерты
│   │   ├── profile.py       # Профиль игрока
│   │   ├── friends.py       # Список друзей
│   │   ├── recent.py        # Недавние игры
│   │   ├── games.py         # Библиотека и случайная игра
│   │   ├── inventory.py     # Инвентарь и поиск по нему
│   │   ├── cs2stats.py      # Статистика CS2
│   │   ├── compare.py       # Сравнение, общие игры/друзья
│   │   ├── leaderboard.py   # Топ друзей по игре
│   │   ├── favorites.py     # Добавление/удаление из избранного
│   │   ├── online_alert.py  # Управление онлайн-алертами
│   │   └── price_tracker.py # Трекер цен на предметы
│   ├── keyboards/
│   │   └── inline.py        # Все клавиатуры и классы CallbackData
│   └── states.py            # Состояния FSM
├── services/
│   ├── steam.py             # Обёртка над Steam Web API и Community API
│   ├── storage.py           # JSON-хранилище (избранное, алерты)
│   └── notifier.py          # Фоновый мониторинг и отправка уведомлений
├── utils/
│   └── formatters.py        # Форматирование профилей и дат
└── data/                    # Автосоздаётся при первом запуске
    ├── favorites.json
    ├── online_alerts.json
    ├── price_alerts.json
    ├── last_seen.json
    └── last_online.json
```

### 🚀 Установка и запуск

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/Lesaght/botSteam.git
cd botSteam
```

#### 2. Создать виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Настроить файл `.env`
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
STEAM_API_KEY=ваш_ключ_Steam_Web_API
```

- **Токен Telegram**: получить у [@BotFather](https://t.me/BotFather)
- **Ключ Steam API**: получить на [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)

#### 4. Запустить бота
```bash
python main.py
```

### 🛠 Технологический стек

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Python | 3.11+ | Язык программирования |
| aiogram | 3.29.0 | Telegram Bot Framework |
| aiohttp | 3.14.1 | Асинхронные HTTP-запросы к Steam API |
| aiofiles | 25.1.0 | Асинхронная работа с файлами |
| python-dotenv | 1.2.2 | Загрузка переменных окружения |
| certifi | latest | SSL-сертификаты (обход проблем macOS) |

### 📡 Используемые API

**Steam Web API** (`api.steampowered.com`)
- `ISteamUser/GetPlayerSummaries` — данные профиля
- `ISteamUser/GetFriendList` — список друзей
- `ISteamUser/GetPlayerBans` — VAC и игровые баны
- `ISteamUser/ResolveVanityURL` — резолв никнеймов в SteamID64
- `IPlayerService/GetOwnedGames` — библиотека игр
- `IPlayerService/GetRecentlyPlayedGames` — недавние игры
- `IPlayerService/GetSteamLevel` — уровень Steam
- `ISteamUserStats/GetUserStatsForGame` — статистика CS2

**Steam Community API**
- `steamcommunity.com/inventory/{steamid}/{appid}/{contextid}` — инвентарь
- `steamcommunity.com/market/priceoverview/` — рыночные цены предметов

### ⚙️ Технические детали

- **Параллельные запросы** — `asyncio.gather()` для одновременного получения данных профиля, уровня, банов
- **Ограничение частоты запросов** — `asyncio.Semaphore(5)` при загрузке цен инвентаря + задержка 300 мс между запросами
- **FSM (конечные автоматы)** — aiogram FSM для пошагового ввода (поиск профиля, сравнение, трекер цен)
- **Фоновый мониторинг** — `asyncio.create_task()` запускает notifier параллельно с polling-ом
- **Хранилище** — JSON-файлы в папке `data/`, асинхронное чтение/запись через aiofiles
- **SSL на macOS** — certifi CA bundle для решения проблем с системными сертификатами Python

### 📋 Ограничения и лимиты

| Параметр | Значение |
|----------|---------|
| Максимум избранных профилей | 10 |
| Максимум трекеров цен | 20 |
| Топ в инвентаре | 10 предметов |
| Топ в библиотеке | 15 игр |
| Список друзей в топе | до 100 человек |
| Интервал проверки уведомлений | 300 секунд |

---

<div align="center">

### 🚀 Ready to use? Start with `/start` in Telegram!

### 🚀 Готов к использованию? Начните с `/start` в Telegram!

---

Made with ❤️ by [Lesaght](https://github.com/Lesaght)

</div>