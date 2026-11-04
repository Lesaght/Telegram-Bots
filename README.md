# Telegram Bots

A monorepo containing independent Telegram bot projects. Each project lives in its own directory and keeps its own dependencies and setup instructions.

## Projects

| Directory | Description |
|---|---|
| [scanPDF-bot](scanPDF-bot/) | Turns photos into PDF scans with image processing |
| [BOT-Weather](BOT-Weather/) | Weather information bot |
| [Generate-password-bot](Generate-password-bot/) | Password generator bot |
| [Reminder-Bot](Reminder-Bot/) | Reminder and scheduling bot |
| [BotTranslator](BotTranslator/) | OCR, translation, speech-to-text and text-to-speech |
| [botSteam](botSteam/) | Steam profiles, games, inventory and activity bot |
| [Meme-Bot](Meme-Bot/) | Meme bot |

## Working with a project

1. Open the project's directory.
2. Read its README for project-specific setup.
3. Install dependencies from that project's requirements or package file.
4. Configure credentials locally; never commit tokens or secrets.

Projects are independent. This repository does not combine their runtime processes or dependency environments.

## Excluded local and generated files

Environment files, local databases, Python bytecode/cache directories, backup files, and machine-specific metadata are not included. Large binary speech-recognition model artifacts from BotTranslator/model/ are also not included; follow that project's model setup instructions to obtain them.
