from aiogram import types
from aiogram import types, Dispatcher

from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


async def view_tracked(message: types.Message):
    animes = await db.select_users_animes(chat_id=message.chat.id)
    print(animes)
    if animes:
        kbd = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        for anime_name, href, episodes in animes:
            buttons.append(types.InlineKeyboardButton(text=f"{anime_name}\nЭпизоды : {episodes}", url=href))
        kbd.add(*buttons)
        await message.answer("Вот ваши анимешки , добавленные в отслеживаемое", reply_markup=kbd)

    else:
        await message.answer("Вы ещё не добавили не одного аниме в отслеживаемые")


def register_view_tracked(dp: Dispatcher):
    dp.register_message_handler(callback=view_tracked, commands=['view_tracked'], state="*")
