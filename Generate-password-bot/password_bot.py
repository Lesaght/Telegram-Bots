import telebot
import random
import string

BOT_TOKEN = 'your_bot_token'

bot = telebot.TeleBot(BOT_TOKEN)

DEFAULT_LENGTH = 12
DEFAULT_USE_NUMBERS = True
DEFAULT_USE_SYMBOLS = True

user_settings = {}
user_languages = {}

localization = {
    'ru': {
        'start_message': "Привет! Я бот для генерации случайных паролей.\n\nНажмите /options чтобы настроить параметры пароля.",
        'help_message': "Доступные команды:\n/start - Запуск бота\n/help - Показать это сообщение\n/options - Настроить параметры генерации пароля",
        'options_message': "Настройки пароля:",
        'length': "Длина:",
        'numbers': "Цифры:",
        'symbols': "Символы:",
        'on': "Вкл",
        'off': "Выкл",
        'generate': "Сгенерировать пароль",
        'new_length_prompt': "Введите новую длину пароля (число):",
        'invalid_length': "Длина пароля должна быть положительным числом.",
        'invalid_number_format': "Неверный формат числа. Введите число.",
        'length_updated': "Длина пароля установлена на {}.",
        'numbers_updated': "Настройки цифр изменены.",
        'symbols_updated': "Настройки символов изменены.",
        'generating': "Генерирую пароль...",
        'unknown_command': "Неизвестная команда!",
        'generated_password': "Сгенерированный пароль: `{}`",
        'language': "Язык | Language",
        'language_updated': "Язык изменен.",
    },
    'en': {
        'start_message': "Hello! I am a bot for generating random passwords.\n\nPress /options to configure password settings.",
        'help_message': "Available commands:\n/start - Start the bot\n/help - Show this message\n/options - Configure password generation options",
        'options_message': "Password settings:",
        'length': "Length:",
        'numbers': "Numbers:",
        'symbols': "Symbols:",
        'on': "On",
        'off': "Off",
        'generate': "Generate password",
        'new_length_prompt': "Enter the new password length (number):",
        'invalid_length': "Password length must be a positive number.",
        'invalid_number_format': "Invalid number format. Enter a number.",
        'length_updated': "Password length set to {}.",
        'numbers_updated': "Numbers settings changed.",
        'symbols_updated': "Symbols settings changed.",
        'generating': "Generating password...",
        'unknown_command': "Unknown command!",
        'generated_password': "Generated password: `{}`",
        'language': "Language | Язык ",
        'language_updated': "Language changed.",
    },
}

def get_translation(user_id, key):
    language = user_languages.get(user_id, 'ru')
    return localization[language][key]

def get_user_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            'length': DEFAULT_LENGTH,
            'use_numbers': DEFAULT_USE_NUMBERS,
            'use_symbols': DEFAULT_USE_SYMBOLS
        }
    return user_settings[user_id]

def update_user_settings(user_id, setting, value):
    settings = get_user_settings(user_id)
    settings[setting] = value
    user_settings[user_id] = settings  # Обновляем global

def create_settings_keyboard(user_id):
    settings = get_user_settings(user_id)
    lang = user_languages.get(user_id, 'ru')

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(f"{get_translation(user_id, 'length')} {settings['length']}", callback_data="change_length"),
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(f"{get_translation(user_id, 'numbers')} {get_translation(user_id, 'on') if settings['use_numbers'] else get_translation(user_id, 'off')}", callback_data="toggle_numbers"),
        telebot.types.InlineKeyboardButton(f"{get_translation(user_id, 'symbols')} {get_translation(user_id, 'on') if settings['use_symbols'] else get_translation(user_id, 'off')}", callback_data="toggle_symbols"),
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(get_translation(user_id, 'generate'), callback_data="generate_password")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(get_translation(user_id, 'language'), callback_data="change_language")
    )

    return keyboard

def create_language_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("English", callback_data="set_language_en"),
        telebot.types.InlineKeyboardButton("Русский", callback_data="set_language_ru")
    )
    return keyboard

def generate_and_send_password(chat_id):
    user_id = chat_id
    settings = get_user_settings(user_id)
    length = settings['length']
    use_numbers = settings['use_numbers']
    use_symbols = settings['use_symbols']

    characters = string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for i in range(length))
    bot.send_message(chat_id, get_translation(user_id, 'generated_password').format(password), parse_mode="MarkdownV2")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in user_languages:
        user_languages[user_id] = 'ru'  # Язык по умолчанию
    bot.send_message(message.chat.id, get_translation(user_id, 'start_message'),
                     reply_markup=create_settings_keyboard(message.chat.id))  # Отправляем клавиатуру сразу


@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.chat.id
    bot.send_message(message.chat.id, get_translation(user_id, 'help_message'))

@bot.message_handler(commands=['options'])
def options(message):
    user_id = message.chat.id
    bot.send_message(message.chat.id, get_translation(user_id, 'options_message'), reply_markup=create_settings_keyboard(message.chat.id))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if call.data == "change_length":
        bot.answer_callback_query(call.id, get_translation(user_id, 'new_length_prompt'))
        bot.register_next_step_handler(call.message, process_length_step)
    elif call.data == "toggle_numbers":
        settings = get_user_settings(user_id)
        update_user_settings(user_id, 'use_numbers', not settings['use_numbers'])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_settings_keyboard(user_id))
        bot.answer_callback_query(call.id, get_translation(user_id, 'numbers_updated'))
    elif call.data == "toggle_symbols":
        settings = get_user_settings(user_id)
        update_user_settings(user_id, 'use_symbols', not settings['use_symbols'])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_settings_keyboard(user_id))
        bot.answer_callback_query(call.id, get_translation(user_id, 'symbols_updated'))
    elif call.data == "generate_password":
        generate_and_send_password(call.message.chat.id) # Используем оригинальную функцию для генерации
        bot.answer_callback_query(call.id, get_translation(user_id, 'generating')) #  Показываем, что пароль генерируется
    elif call.data == "change_language":
        bot.answer_callback_query(call.id, "Выберите язык:")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_language_keyboard())
    elif call.data == "set_language_en":
        user_languages[user_id] = 'en'
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_settings_keyboard(user_id))
        bot.answer_callback_query(call.id, get_translation(user_id, 'language_updated'))
    elif call.data == "set_language_ru":
        user_languages[user_id] = 'ru'
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_settings_keyboard(user_id))
        bot.answer_callback_query(call.id,  get_translation(user_id, 'language_updated'))
    else:
        bot.answer_callback_query(call.id, get_translation(user_id, 'unknown_command'))

def process_length_step(message):
    user_id = message.chat.id
    try:
        length = int(message.text)
        if length > 0:
            update_user_settings(user_id, 'length', length)
            bot.send_message(message.chat.id, get_translation(user_id, 'length_updated').format(length), reply_markup=create_settings_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, get_translation(user_id, 'invalid_length'), reply_markup=create_settings_keyboard(message.chat.id))
    except ValueError:
        bot.send_message(message.chat.id, get_translation(user_id, 'invalid_number_format'), reply_markup=create_settings_keyboard(message.chat.id))

bot.infinity_polling()
