<!-- ===================== HERO ===================== -->
<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,50:2563EB,100:06B6D4&height=190&section=header&text=Telegram%20Bots&fontSize=54&fontColor=FFFFFF&fontAlignY=38&desc=A%20collection%20of%20useful%20Telegram%20projects&descAlignY=60&descSize=16" width="100%" alt="Telegram Bots banner" />

  <p>
    <strong>🤖 Семь независимых Telegram-ботов в одном месте</strong><br>
    Небольшая коллекция проектов для повседневных задач, экспериментов и автоматизации.
  </p>

  <p>
    <a href="#-проекты"><img src="https://img.shields.io/badge/Проекты-7-2563EB?style=for-the-badge" alt="7 projects"></a>
    <a href="https://github.com/Lesaght/Telegram-Bots"><img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub repository"></a>
    <a href="https://core.telegram.org/bots"><img src="https://img.shields.io/badge/Platform-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
  </p>

  <p>
    <a href="#-проекты">Проекты</a> ·
    <a href="#-быстрый-старт">Быстрый старт</a> ·
    <a href="#-структура">Структура</a> ·
    <a href="#-безопасность">Безопасность</a> ·
    <a href="#-english">English</a>
  </p>
</div>

---

## ✨ О проекте

**Telegram-Bots** — коллекция из семи самостоятельных Telegram-ботов. Каждый проект находится в своей папке, имеет собственный код и зависимости, поэтому его можно изучать, настраивать и запускать отдельно.

> 💡 Это не единое приложение: выбирайте нужного бота и следуйте инструкциям внутри его директории.

## 🚀 Проекты

| Проект | Что умеет |
|:--|:--|
| 📄 **[scanPDF-bot](scanPDF-bot/)** | Превращает изображения в PDF-сканы с помощью инструментов обработки изображений. |
| 🌦️ **[BOT-Weather](BOT-Weather/)** | Помогает узнавать погоду. |
| 🔐 **[Generate-password-bot](Generate-password-bot/)** | Генерирует пароли. |
| ⏰ **[Reminder-Bot](Reminder-Bot/)** | Создаёт напоминания и помогает управлять запланированными уведомлениями. |
| 🌐 **[BotTranslator](BotTranslator/)** | Инструменты перевода, OCR, распознавание речи и преобразование текста в речь. |
| 🎮 **[botSteam](botSteam/)** | Показывает информацию о Steam: профили, игры, инвентарь и активность. |
| 😂 **[Meme-Bot](Meme-Bot/)** | Бот для работы с мемами. |

## ⚡ Быстрый старт

1. Откройте папку понравившегося бота.
2. Прочитайте его `README.md`, если он есть.
3. Установите зависимости из файлов проекта.
4. Создайте локальный `.env` или настройте переменные окружения, если они нужны.
5. Запустите бота по инструкции в его папке.

**Важно:** общего установщика и единой команды запуска нет — каждый бот настраивается и запускается независимо.

## 🗂️ Структура

```text
Telegram-Bots/
├── BOT-Weather/
├── BotTranslator/
├── Generate-password-bot/
├── Meme-Bot/
├── Reminder-Bot/
├── botSteam/
├── scanPDF-bot/
├── .gitignore
└── README.md
```

## 🔒 Безопасность

- Никогда не публикуйте Telegram-токены, API-ключи, пароли и другие секреты.
- Храните локальные настройки в `.env` и не добавляйте этот файл в Git.
- Если секрет попал в публичный доступ, немедленно отзовите его и создайте новый.
- Перед запуском проверяйте, какие разрешения и API-доступы запрашивает конкретный бот.

## 📝 Примечания

- У каждого бота собственные зависимости и процесс запуска.
- Локальные базы данных, кэши, резервные копии и файлы конкретной машины не входят в репозиторий.
- Большие бинарные файлы речевых моделей для **BotTranslator** здесь не хранятся. Способ их получения описывается в самом проекте.

## 🤝 Вклад в проект

Буду рад предложениям, исправлениям и улучшениям! При отправке изменений старайтесь ограничивать их папкой соответствующего бота и обновлять документацию вместе с кодом.

---

## 🇬🇧 English

**Telegram-Bots** is a collection of seven independent Telegram bot projects. Each bot lives in its own directory and has its own code, dependencies, and setup instructions.

### Projects

| Project | Description |
|:--|:--|
| [📄 scanPDF-bot](scanPDF-bot/) | Converts images into PDF scans using image-processing tools. |
| [🌦️ BOT-Weather](BOT-Weather/) | A Telegram bot for checking the weather. |
| [🔐 Generate-password-bot](Generate-password-bot/) | Generates passwords. |
| [⏰ Reminder-Bot](Reminder-Bot/) | Creates reminders and manages scheduled notifications. |
| [🌐 BotTranslator](BotTranslator/) | Translation tools with OCR, speech recognition, and text-to-speech. |
| [🎮 botSteam](botSteam/) | Shows Steam profiles, games, inventory, and activity. |
| [😂 Meme-Bot](Meme-Bot/) | A bot for working with memes. |

### Getting started

1. Choose a bot directory.
2. Read its README and project-specific instructions.
3. Install the dependencies listed in that project.
4. Configure required tokens and API keys through environment variables or a local `.env` file.
5. Run the bot using its documented entry point.

There is no shared root-level installer or launcher. Each bot is maintained and run independently.

### Contributing

Bug reports, ideas, code improvements, and documentation updates are welcome. Keep changes scoped to the relevant bot and document any setup or dependency changes.

---

<div align="center">
  <sub>Built with ❤️ for learning, automation, and Telegram bot experiments.</sub><br>
  <sub>Сделано с ❤️ для обучения, автоматизации и экспериментов с Telegram.</sub>
</div>
