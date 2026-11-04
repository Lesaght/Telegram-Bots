from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import crud

router = Router()


@router.callback_query(F.data.startswith("moderate_"))
async def process_moderation(callback: CallbackQuery):
    if not await crud.is_user_moderator(callback.from_user.id):
        await callback.answer("У вас нет прав модератора!", show_alert=True)
        return

    parts = callback.data.split(":")

    if len(parts) != 2:
        await callback.answer("Некорректные данные", show_alert=True)
        return

    action = parts[0]
    meme_id = int(parts[1])

    meme = await crud.get_meme_by_id(meme_id)

    if not meme:
        await callback.answer("Мем не найден", show_alert=True)
        return

    if meme['status'] != 'PENDING':
        await callback.answer("Мем уже обработан", show_alert=True)
        return

    if action == "moderate_approve":
        await crud.update_meme_status(meme_id, 'APPROVED', callback.from_user.id)

        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n✅ Одобрено модератором @{callback.from_user.username}",
            reply_markup=None
        )

        await callback.answer("Мем одобрен!")

    elif action == "moderate_reject":
        await crud.update_meme_status(meme_id, 'REJECTED', callback.from_user.id)

        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n❌ Отклонено модератором @{callback.from_user.username}",
            reply_markup=None
        )

        await callback.answer("Мем отклонен!")
