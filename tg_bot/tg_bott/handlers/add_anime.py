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


async def add_anime(message: types.Message, state: FSMContext):
    await message.answer(
        f'Инструкция : \n'
        f'Чтобы добавить аниме в отслеживаемые, тебе нужно зайти на этот сайтик https://animego.org/ и найти нужную анимку\n'
        f'Далее скидываешь ссылку мне :)')
    await message.answer(f'Скидывай ссылку')
    await state.set_state(GetHref.waiting_for_href.state)


async def add(message: types.Message, state: FSMContext):
    if message.text.startswith('https://animego.org/'):
        await state.update_data(href=message.text)
        await func()
        user_data = await state.get_data()
        print(f'{message.chat.id}  :  {user_data["href"]}')
        async with aiohttp.ClientSession() as session:
            parser = AParser(session=session)
            if await parser.check(user_data["href"],type='anime'):
                data_of_anime = await parser.get_page(url=message.text,type='anime')
                check = await db.add_users_anime(await db.add_user(chat_id=message.chat.id),
                                                 await db.add_title(href=message.text, name= data_of_anime[0],episodes=data_of_anime[1],type= 'anime'))
                if check:
                    await message.reply("Аниме добавлено в отслеживаемые")
                else:
                    await message.reply('Вы уже добавили это аниме')
                await state.finish()
            else:
                await message.reply('Это аниме не идет в онгоинге')

    else:
        await message.reply('Хм, это непохоже на подходящую ссылку')
        await state.finish()


def register_add_anime(dp: Dispatcher):
    dp.register_message_handler(callback=add_anime, commands=['add_anime'], state="*")
    dp.register_message_handler(callback=add, state=GetHref.waiting_for_href)
