from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup
# from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tg_bot.tg_bott.handlers.add_anime import add_anime, GetHref

GetHref = GetHref()


async def bot_start(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="Посмотреть список отслеживаемых онгоингов", callback_data="see"),
        types.InlineKeyboardButton(text="Добавить аниме в отслеживаемое", callback_data="add_anime"),
        types.InlineKeyboardButton(text="Удалить аниме из отслеживаемого", callback_data="delete_anime")
    ]
    kbd = types.InlineKeyboardMarkup(row_width=1)
    kbd.add(*buttons)
    await message.answer(
        f'Привет друг!\nЯ - аниме-бот , который поможет тебе не забыть о том , что вышла новая серия твоего любимого тайтла:)')
    await message.answer(f'Ты можешь :', reply_markup=kbd)


async def bot_add_anime(call: types.CallbackQuery, state):
    if call.data == "add_anime":
        await add_anime(message=call.message, state=state)
        await call.answer("Погнали!", show_alert=False)


def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'], state='*')
    dp.register_callback_query_handler(bot_add_anime, state='*')
