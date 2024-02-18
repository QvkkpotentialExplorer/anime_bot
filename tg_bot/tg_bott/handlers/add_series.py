import aiohttp
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from parser.new_parser import AParser
from tg_bot.tg_bott.db.bot_db import DataBase, func

dict_of_users = {}

db = DataBase()


class GetHref(StatesGroup):
    waiting_for_href = State()
    # waiting_for_status = []


async def add_series(message: types.Message, state: FSMContext):
    await message.answer(
        f'Инструкция : \n'
        f'Чтобы добавить сериал в отслеживаемые, тебе нужно зайти на этот сайтик: https://www.film.ru/serials/ и найти нужный сериал\n'
        f'Далее скидываешь ссылку мне :)')
    await message.answer(f'Скидывай ссылку')
    await state.set_state(GetHref.waiting_for_href.state)


async def add(message: types.Message, state: FSMContext):
    if message.text.startswith('https://www.film.ru/serials/'):
        content_type = 'series'
        await state.update_data(href=message.text)
        user_data = await state.get_data()
        print(f'{message.chat.id}  :  {user_data["href"]}')
        async with aiohttp.ClientSession() as session:
            parser = AParser(session=session)
            if await parser.check(user_data["href"],content_type=content_type):
                data_of_series = await parser.get_page(url=message.text,content_type="series")
                check = await db.add_users_title(await db.add_user(chat_id=message.chat.id),
                                                 await db.add_title(href=message.text, name= data_of_series[0],episodes=data_of_series[1],content_type= 'series'))
                if check:
                    await message.reply("Сериал добавлен в отслеживаемые")
                else:
                    await message.reply('Вы уже добавили этот сериал')
                await state.finish()
            else:
                await message.reply('Этот сериал не идет в онгоинге')

    else:
        await message.reply('Хм, это непохоже на подходящую ссылку')
        await state.finish()


def register_add_series(dp: Dispatcher):
    dp.register_message_handler(callback=add_series, commands=['add_series'], state="*")
    dp.register_message_handler(callback=add, state=GetHref.waiting_for_href)
