from aiogram import types, Dispatcher


dict_of_users = {}
async def bot_ongoing(message: types.Message):
     if message.text.startswith('https://animego.org/anime'):
         await message.reply('Ссылку получил')
         dict_of_users[message.text] = message.chat.id
         print(dict_of_users)


def register_ongoing(dp: Dispatcher):
    dp.register_message_handler(callback=bot_ongoing)
