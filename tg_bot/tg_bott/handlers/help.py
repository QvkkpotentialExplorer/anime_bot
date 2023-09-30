from aiogram import types, Dispatcher



async def help(message: types.Message):
    await message.answer('Меню комманд:\n <b>/start</b> - <i>старт</i>\n <b>/help</b> - <i>справка</i>\n'
                         '<b>/get_ID</b> - <i>получить свой ID</i>')

def register_help_commands(dp: Dispatcher):
    dp.register_message_handler(help, commands=['help'])
    # dp.register_message_handler(get_ID ,commands=['get_ID'])