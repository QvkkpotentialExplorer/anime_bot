from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


class GetCallback(StatesGroup):
    waiting_for_callback = State()


async def delete_anime(message: types.Message, state: FSMContext):
    animes = await db.select_users_animes(chat_id=message.chat.id)
    if animes:

        buttons = []
        for anime_name, href, episodes in animes:
            buttons.append(types.InlineKeyboardButton(text=f"{anime_name}", callback_data=anime_name))
        kbd = types.InlineKeyboardMarkup(row_width=1)
        kbd.add(*buttons)
        print(kbd)
        await message.answer(
            "Вот ваши анимешки , добавленные в отслеживаемое.\n"
            "Нажмите на тайтл , о выходе новых серий котрого, вы больше не хотите знать  ",
            reply_markup=kbd)
        await state.set_state(GetCallback.waiting_for_callback.state)
        print(state)
    else:
        await message.answer("Вы ещё не добавили не одного аниме в отслеживаемые")


async def delete(call: types.CallbackQuery, state: FSMContext):
    print(call.data)
    anime_name = await db.delete_users_anime(chat_id=call.message.chat.id, anime_name=call.data)
    await call.message.answer(f'Аниме: {anime_name} было удалено из ваших отслеживаемых')
    await call.answer()
    await state.finish()

def register_delete_anime(dp: Dispatcher):
    dp.register_message_handler(delete_anime, commands=['delete'], state="*")
    dp.register_callback_query_handler(delete, state=GetCallback.waiting_for_callback)
