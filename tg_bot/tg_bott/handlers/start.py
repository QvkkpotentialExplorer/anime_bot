from aiogram import types, Dispatcher

from aiogram.dispatcher.filters import CommandStart


async def bot_start(message: types.Message):
    buttons = [
        types.KeyboardButton(text="Отслеживать аниме"),
        types.KeyboardButton(text="Отслеживать сериал"),
        types.KeyboardButton(text="Что я отслеживаю?"),
        types.KeyboardButton(text="Перестать отслеживать")
    ]
    kbd = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kbd.add(*buttons)
    await message.answer(
        text=f'Привет друг!\n'
             f'Я - Notific, я помогу тебе не забыть о том, что вышла новая серия твоего любимого тайтла:)\n'
             f'Ты можешь:',
        reply_markup=kbd
    )


def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, CommandStart())
