
import aiohttp
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, message

from parser.new_parser import AParser
from tg_bot.tg_bott.db.bot_db import DataBase, func

dict_of_users = {}

async def add_series(message : types.Message):
    print('sdfsdfsd')
    await message.answer('Я пока не работаю')

def register_add_series(dp:Dispatcher):
    dp.register_message_handler(add_series,commands=['add_series'])
