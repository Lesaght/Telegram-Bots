from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from keyboards import get_rating_keyboard, get_rated_keyboard
from config import settings

router = Router()


class UploadStates(StatesGroup):
    waiting_for_file = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await crud.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я бот для работы с мемами.\n\n"
        "Доступные команды:\n"
        "/upload - Загрузить мем на модерацию\n"
        "/meme - Посмотреть случайный мем\n\n"
        "Все загруженные мемы проходят модерацию перед публикацией."
    )


@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext):
    if await crud.is_user_banned(message.from_user.id):
        await message.answer("Вы заблокированы и не можете загружать мемы.")
        return

    await message.answer(
        "Отправьте мне фото или видео, которое вы хотите загрузить.\n"
        "После отправки мем будет отправлен на модерацию."
    )
    await state.set_state(UploadStates.waiting_for_file)


@router.message(UploadStates.waiting_for_file, F.content_type.in_([ContentType.PHOTO, ContentType.VIDEO]))
async def process_file_upload(message: Message, state: FSMContext):
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id

    if not file_id:
        await message.answer("Пожалуйста, отправьте фото или видео.")
        return

    user = await crud.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    meme = await crud.add_new_meme(file_id=file_id, user_id=user['id'])

    await message.answer("Ваш мем отправлен на модерацию!")

    await state.clear()

    from main import bot
    from keyboards import get_moderation_keyboard

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if message.photo:
        await bot.send_photo(
            chat_id=settings.moderation_chat_id,
            photo=file_id,
            caption=f"Новый мем от {username}\nID мема: {meme['id']}",
            reply_markup=get_moderation_keyboard(meme['id'])
        )
    elif message.video:
        await bot.send_video(
            chat_id=settings.moderation_chat_id,
            video=file_id,
            caption=f"Новый мем от {username}\nID мема: {meme['id']}",
            reply_markup=get_moderation_keyboard(meme['id'])
        )


@router.message(UploadStates.waiting_for_file)
async def process_invalid_upload(message: Message):
    await message.answer("Пожалуйста, отправьте фото или видео.")


@router.message(Command("meme"))
async def cmd_meme(message: Message):
    if await crud.is_user_banned(message.from_user.id):
        await message.answer("Вы заблокированы.")
        return

    await send_random_meme(message)


async def send_random_meme(message: Message):
    meme = await crud.get_random_approved_meme()

    if not meme:
        await message.answer("Пока нет одобренных мемов. Попробуйте позже.")
        return

    from main import bot

    try:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=meme['file_id'],
            caption="Оцените мем:",
            reply_markup=get_rating_keyboard(meme['id'])
        )
    except Exception:
        try:
            await bot.send_video(
                chat_id=message.chat.id,
                video=meme['file_id'],
                caption="Оцените мем:",
                reply_markup=get_rating_keyboard(meme['id'])
            )
        except Exception as e:
            await message.answer(f"Ошибка при отправке мема: {str(e)}")


@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery):
    await callback.answer()

    if await crud.is_user_banned(callback.from_user.id):
        await callback.message.edit_caption(
            caption="Вы заблокированы.",
            reply_markup=None
        )
        return

    parts = callback.data.split(":")

    if len(parts) == 2:
        action = parts[0]
        meme_id = int(parts[1])

        if action == "rate_up":
            await crud.update_or_create_rating(meme_id, callback.from_user.id, 1)
            await callback.message.edit_caption(
                caption="Оценка принята! 👍",
                reply_markup=get_rated_keyboard()
            )
        elif action == "rate_down":
            await crud.update_or_create_rating(meme_id, callback.from_user.id, -1)
            await callback.message.edit_caption(
                caption="Оценка принята! 👎",
                reply_markup=get_rated_keyboard()
            )


@router.callback_query(F.data == "next_meme")
async def process_next_meme(callback: CallbackQuery):
    await callback.answer()

    meme = await crud.get_random_approved_meme()

    if not meme:
        await callback.message.edit_caption(
            caption="Пока нет одобренных мемов. Попробуйте позже.",
            reply_markup=None
        )
        return

    from main import bot

    try:
        await callback.message.delete()
    except Exception:
        pass

    try:
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=meme['file_id'],
            caption="Оцените мем:",
            reply_markup=get_rating_keyboard(meme['id'])
        )
    except Exception:
        try:
            await bot.send_video(
                chat_id=callback.message.chat.id,
                video=meme['file_id'],
                caption="Оцените мем:",
                reply_markup=get_rating_keyboard(meme['id'])
            )
        except Exception:
            pass


@router.callback_query(F.data == "rated")
async def process_rated(callback: CallbackQuery):
    await callback.answer("Оценка уже принята")
