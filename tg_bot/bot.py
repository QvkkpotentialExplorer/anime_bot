import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tg_bot.tg_bott.db.bot_db import DataBase
from tg_bot.tg_bott.handlers.add_anime import register_add_anime
from tg_bott.config import load_config

# from tg_bott.handlers.echo import register_echo
from tg_bott.handlers.help import register_help_commands


from tg_bott.handlers.start import register_start

logger = logging.getLogger(__name__)
db = DataBase()

def register_middleware(dp):
    #dp.setup_middleware(...)
    pass


def register_filters(dp):
   pass
def register_hendler(dp):
    register_start(dp)

    register_add_anime(dp)
    register_help_commands(dp)
    # register_echo(dp)
    # register_ongoing(dp)







async def main():
    db.create_table()
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    config = load_config(path='.env')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    storage = RedisStorage2() if config.tg_bot.user_redis else MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    bot['config'] = config

    register_middleware(dp)
    register_filters(dp)
    register_hendler(dp)
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main=main())
    except(KeyboardInterrupt, SystemExit,RuntimeError):
        logger.error('Все кончается')
