from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


class GetCallback(StatesGroup):
    waiting_for_callback = State()


async def delete_title(message: types.Message):
    animes = await db.select_users_titles(chat_id=message.chat.id, content_type="anime")
    series = await db.select_users_titles(chat_id=message.chat.id, content_type="series")
    if not animes and not series:
        await message.answer("Вы ещё не добавили не одного аниме или сериала в отслеживаемые")
    else:
        kbd_delete = types.InlineKeyboardMarkup(row_width=1)
        if animes:
            for title_id, name, href, episodes in animes:
                kbd_delete.add(types.InlineKeyboardButton(text=f"Аниме {name}", callback_data=f'{title_id},anime'))
        if series:
            for title_id, name, href, episodes in series:
                kbd_delete.add(types.InlineKeyboardButton(text=f"Сериал {name}", callback_data=f'{title_id},series'))

        await message.answer("Что удалить?", reply_markup=kbd_delete)
        # await state.set_state(GetCallback.waiting_for_callback.state)


async def delete_cb(call: types.CallbackQuery, state: FSMContext):
    print(call.data)
    print("I'm delete_callback")
    title_name = await db.delete_users_title(
        chat_id=call.message.chat.id,
        title_id=call.data.split(',')[0],
        content_type=call.data.split(',')[1]
    )
    await call.answer(f'Удалено: {title_name}', show_alert=False)
    await state.finish()


def register_delete_title(dp: Dispatcher):
    dp.register_message_handler(delete_title, Text('Перестать отслеживать', ignore_case=True))
    dp.register_callback_query_handler(delete_cb)#, state=GetCallback.waiting_for_callback)
