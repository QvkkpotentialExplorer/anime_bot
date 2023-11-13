
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from parser.check_py import check
from tg_bot.tg_bott.db.bot_db import DataBase

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton(text='Онгоинг'), KeyboardButton(text='Анонс'))

dict_of_users = {}

db = DataBase()

class GetHref(StatesGroup):
    waiting_for_href = State()
    # waiting_for_status = []


async def add_anime(message: types.Message, state: FSMContext):
    await message.answer(
        f'Инструкция : \nЧтобы добавить аниме в отслеживаемые, тебе нужно зайти на этот сайтик https://animego.org/ и найти нужную анимку\n'
        f'Далее скидываешь ссылку мне :)', reply_markup=kb)
    await message.answer(f'Скидывай ссылку')
    await state.set_state(GetHref.waiting_for_href.state)


async def add(message: types.Message, state: FSMContext):
    if message.text.startswith('https://animego.org/'):
        await state.update_data(href=message.text)
        user_data = await state.get_data()
        print(f'{message.chat.id}  :  {user_data["href"]}')
        if await check(user_data["href"]): # Проверка , выходит ли аниме в онгоинге
            db.add_users_anime( db.add_user(chat_id=message.chat.id ),db.add_anime(href = message.text))

            await state.finish()
        else:
            await message.reply('Это аниме не идет в онгинге')

    else:
        await message.reply('Хм, это непохоже на подходящую ссылку')
        return







def register_add_anime(dp: Dispatcher):
    dp.register_message_handler(callback=add_anime, commands=['add_anime'], state="*")
    dp.register_message_handler(callback=add, state=GetHref.waiting_for_href)
