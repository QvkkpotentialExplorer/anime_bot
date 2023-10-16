from aiogram import types, Dispatcher
# from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton(text='Онгоинг'), KeyboardButton(text='Анонс'))

async def bot_start(message: types.Message):
    await message.answer(f'Привет друг!\nЯ - аниме-бот , который поможет тебе не забыть о том , что вышла новая серия твоего любимого тайтла:)', reply_markup=kb)
    await message.answer(f'---------')



def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start,commands=['start'])

