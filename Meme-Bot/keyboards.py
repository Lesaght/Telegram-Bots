from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_rating_keyboard(meme_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👍", callback_data=f"rate_up:{meme_id}"),
        InlineKeyboardButton(text="👎", callback_data=f"rate_down:{meme_id}"),
        InlineKeyboardButton(text="➡️", callback_data="next_meme")
    )

    return builder.as_markup()


def get_moderation_keyboard(meme_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"moderate_approve:{meme_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"moderate_reject:{meme_id}")
    )

    return builder.as_markup()


def get_rated_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Оценка принята", callback_data="rated"),
        InlineKeyboardButton(text="➡️ Следующий мем", callback_data="next_meme")
    )

    return builder.as_markup()
