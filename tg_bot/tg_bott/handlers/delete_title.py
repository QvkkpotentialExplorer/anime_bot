from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


class GetCallback(StatesGroup):
    waiting_for_callback = State()


async def delete_title(message: types.Message, state: FSMContext):
    animes = await db.select_users_titles(chat_id=message.chat.id,content_type="anime")
    print(animes)
    series = await db.select_users_titles(chat_id=message.chat.id,content_type="series")
    kbd = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    if animes:
        for title_id,name, href, episodes in animes:
            print(name,href)
            buttons.append(types.InlineKeyboardButton(text=f"Аниме {name}", callback_data=f'{title_id},anime'))

        kbd.add(*buttons)
        print(kbd)
        buttons=[]
    if series:
        for title_id,name, href, episodes in series:
            buttons.append(types.InlineKeyboardButton(text=f"Сериал {name}", callback_data= f'{title_id},series'))
        kbd.add(*buttons)
    if buttons == []:
        await message.answer("Вы ещё не добавили не одного аниме или сериала в отслеживаемые")
    else:
        await message.answer(
            "Вот ваши анимешки и сериалы, добавленные в отслеживаемое.\n"
            "Нажмите на тайтл , о выходе новых серий которого, вы больше не хотите знать  ",
            reply_markup=kbd)
        await state.set_state(GetCallback.waiting_for_callback.state)
        print(state)



async def delete(call: types.CallbackQuery, state: FSMContext):
    print(call.data)
    title_name = await db.delete_users_title(chat_id=call.message.chat.id,title_id=call.data.split(',')[0],content_type=call.data.split(',')[1])
    await call.message.answer(f'{title_name[0]} было удалено из ваших отслеживаемых')
    await call.answer()
    await state.finish()

def register_delete_title(dp: Dispatcher):
    dp.register_message_handler(delete_title, commands=['delete_title'], state="*")
    dp.register_callback_query_handler(delete, state=GetCallback.waiting_for_callback)
