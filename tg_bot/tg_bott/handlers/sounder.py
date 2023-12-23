import aiohttp
from aiogram import types

from parser.new_parser import AParser
from tg_bot.tg_bott.db.bot_db import DataBase

db = DataBase()


async def sounder(message: types.Message):
    async with aiohttp.ClientSession() as session:
        parser = AParser(session=session)
        lst_of_anime = await db.select_anime()
        await parser.gather_data(lst_anime=lst_of_anime)  # Собираем новые данные об аниме
        await parser.find_new_series(lst_of_anime=lst_of_anime)  # Ищет новые серии и сипользует функц db.wrote()
    users_for_message = await db.for_sounder()
    for users, anime in users_for_message:
        await message.bot.send_message(chat_id=users, text=f'{anime[1]} вышла новая серия {anime[2]} \n {[anime[0]]}')
