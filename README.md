# 🤖 Telegram Bots Collection

<p align="center">
  <strong>A collection of independent Telegram bot projects in one repository.</strong><br>
  <strong>Коллекция независимых проектов Telegram-ботов в одном репозитории.</strong>
</p>

<p align="center">
  <a href="#-projects--проекты">Projects</a> ·
  <a href="#-getting-started">Getting started</a> ·
  <a href="#-проекты">Русский</a> ·
  <a href="#-запуск-проекта">Запуск</a>
</p>

---

## 🇬🇧 English

A home for seven Telegram bot projects, organized into separate directories for easier navigation, development, and maintenance. Each bot remains an independent project with its own code and dependencies.

### ✨ Projects

| Project | Description |
|---|---|
| [📄 scanPDF-bot](scanPDF-bot/) | Turns images into PDF scans using image-processing tools. |
| [🌦️ BOT-Weather](BOT-Weather/) | A Telegram bot for checking the weather. |
| [🔐 Generate-password-bot](Generate-password-bot/) | Generates passwords. |
| [⏰ Reminder-Bot](Reminder-Bot/) | Helps create reminders and manage scheduled notifications. |
| [🌐 BotTranslator](BotTranslator/) | Translation toolkit with OCR, speech-to-text, and text-to-speech features. |
| [🎮 botSteam](botSteam/) | Provides Steam-related information, including profiles, games, inventory, and activity. |
| [😂 Meme-Bot](Meme-Bot/) | A bot for working with memes. |

### 🚀 Getting started

1. **Choose a bot** from the project list and open its directory.
2. **Read its README** (if provided) for project-specific instructions.
3. **Set up its environment** and install the dependencies listed in that project's dependency files.
4. **Configure credentials** such as Telegram bot tokens and API keys using local environment variables or a local `.env` file, as required by the project.
5. **Run the bot** using the entry point and instructions documented in its directory.

> There is no single root-level installer or launcher: each bot is maintained and run independently.

### 🧰 Repository layout

```text
Telegram-Bots/
├── scanPDF-bot/
├── BOT-Weather/
├── Generate-password-bot/
├── Reminder-Bot/
├── BotTranslator/
├── botSteam/
├── Meme-Bot/
├── .gitignore
└── README.md
```

### 🔒 Security

- Never commit Telegram tokens, API keys, passwords, or other secrets.
- Keep local configuration files (such as `.env`) out of version control.
- If a token or key is exposed, revoke it and generate a replacement.

### 📝 Notes

- The projects are grouped in one repository, but their codebases, dependencies, and runtime processes remain separate.
- Local databases, caches, bytecode, backups, and machine-specific files are intentionally excluded.
- Large binary speech-model artifacts for **BotTranslator** are not stored here. Follow that project's setup instructions to obtain the required models.

### 🤝 Contributions

Improvements, bug fixes, and documentation updates are welcome. When contributing, keep changes scoped to the relevant bot directory and include any setup or dependency changes.

---

## 🇷🇺 Русский

Этот репозиторий объединяет семь Telegram-ботов, каждый из которых находится в отдельной папке. Такая структура упрощает навигацию и поддержку проектов, сохраняя их независимость: у каждого бота свой код, зависимости и инструкции по запуску.

## ✨ Проекты

| Проект | Описание |
|---|---|
| [📄 scanPDF-bot](scanPDF-bot/) | Преобразует изображения в PDF-сканы с помощью обработки изображений. |
| [🌦️ BOT-Weather](BOT-Weather/) | Telegram-бот для получения информации о погоде. |
| [🔐 Generate-password-bot](Generate-password-bot/) | Генерирует пароли. |
| [⏰ Reminder-Bot](Reminder-Bot/) | Помогает создавать напоминания и управлять запланированными уведомлениями. |
| [🌐 BotTranslator](BotTranslator/) | Инструменты перевода: OCR, распознавание речи и преобразование текста в речь. |
| [🎮 botSteam](botSteam/) | Показывает информацию о Steam: профили, игры, инвентарь и активность. |
| [😂 Meme-Bot](Meme-Bot/) | Бот для работы с мемами. |

## 🚀 Запуск проекта

1. **Выберите бота** из списка выше и откройте его папку.
2. **Изучите README** внутри папки, если он есть: там могут быть инструкции именно для этого проекта.
3. **Подготовьте окружение** и установите зависимости, указанные в файлах проекта.
4. **Настройте доступы** — токены Telegram-ботов и API-ключи — через локальные переменные окружения или файл `.env`, если этого требует проект.
5. **Запустите бота** согласно инструкциям и используемой точке входа в его папке.

> Единого установщика или команды запуска для всего репозитория нет: каждый бот устанавливается и запускается отдельно.

## 🧰 Структура репозитория

```text
Telegram-Bots/
├── scanPDF-bot/
├── BOT-Weather/
├── Generate-password-bot/
├── Reminder-Bot/
├── BotTranslator/
├── botSteam/
├── Meme-Bot/
├── .gitignore
└── README.md
```

## 🔒 Безопасность

- Не добавляйте в Git токены Telegram, API-ключи, пароли и другие секретные данные.
- Не загружайте в репозиторий локальные файлы конфигурации, например `.env`.
- Если токен или ключ стал публичным, отзовите его и создайте новый.

## 📝 Примечания

- Проекты собраны в одном репозитории, но их исходный код, зависимости и процессы запуска остаются независимыми.
- Локальные базы данных, кэши, байткод, резервные копии и файлы, зависящие от конкретной машины, намеренно не включены.
- Большие бинарные файлы речевых моделей **BotTranslator** не хранятся в этом репозитории. Для их получения следуйте инструкциям внутри проекта.

## 🤝 Участие в разработке

Буду рад улучшениям, исправлениям ошибок и обновлениям документации. По возможности ограничивайте изменения папкой соответствующего бота и не забывайте обновлять инструкции и зависимости, если они меняются.

---

<p align="center">
  <sub>Made with ❤️ for Telegram bot experiments and projects.</sub><br>
  <sub>Сделано с ❤️ для экспериментов и проектов с Telegram-ботами.</sub>
</p>
