from aiogram import types
from aiogram import types, Dispatcher

from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


async def view_tracked(message: types.Message):
    animes = await db.select_users_titles(chat_id=message.chat.id, content_type='anime')
    series = await db.select_users_titles(chat_id=message.chat.id, content_type='series')
    print(series)
    print(series)
    kbd = types.InlineKeyboardMarkup(row_width=1)
    if animes:
        buttons = []
        for name, href, episodes in animes:
            buttons.append(types.InlineKeyboardButton(text=f"Аниме {name}\nЭпизоды : {episodes}", url=href))
        kbd.add(*buttons)
    if series:
        for name, href, episodes in series:
            buttons = []
            buttons.append(types.InlineKeyboardButton(text=f" Сериал {name}\nЭпизоды : {episodes}", url=href))
            kbd.add(*buttons)
    if kbd == None:
        await message.answer("Вы ещё не добавили не одного сериала или аниме в отслеживаемые")
    else:
        await message.answer("Вот ваши отслеживаемые аниме и сериалы", reply_markup=kbd)


def register_view_tracked(dp: Dispatcher):
    dp.register_message_handler(callback=view_tracked, commands=['view_tracked'], state="*")
