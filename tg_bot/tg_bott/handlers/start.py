from aiogram import types, Dispatcher

from tg_bot.tg_bott.handlers.add_anime import add_anime
from tg_bot.tg_bott.handlers.delete_anime import delete_anime
from tg_bot.tg_bott.handlers.view_tracked import view_tracked


# from aiogram.dispatcher.filters import CommandStart

# GetHref = GetHref()
# GetCallback = GetCallback()


async def bot_start(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="Посмотреть список отслеживаемых онгоингов", callback_data="view_tracked"),
        types.InlineKeyboardButton(text="Добавить аниме в отслеживаемое", callback_data="add_anime"),
        types.InlineKeyboardButton(text="Удалить аниме из отслеживаемого", callback_data="delete_anime")
        types.InlineKeyboardButton(text="Добавить сериал в отслеживаемое",callback_data="add_series")
    ]
    kbd = types.InlineKeyboardMarkup(row_width=1)
    kbd.add(*buttons)
    await message.answer(
        f'Привет друг!\nЯ - аниме-бот , который поможет тебе не забыть о том , что вышла новая серия твоего любимого тайтла:)')
    await message.answer(f'Ты можешь :', reply_markup=kbd)


async def bot_callback_handlers(call: types.CallbackQuery, state):
    if call.data == "add_anime":
        await add_anime(message=call.message, state=state)

    elif call.data == "view_tracked":
        await view_tracked(message=call.message)
    elif call.data == "delete_anime":
        await delete_anime(message=call.message, state=state)
    await call.answer()


def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'], state='*')
    dp.register_callback_query_handler(bot_callback_handlers, state='*', )
