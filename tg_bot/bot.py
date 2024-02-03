import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from parser.new_parser import AParser
from tg_bot.tg_bott.db.bot_db import DataBase
from tg_bot.tg_bott.handlers.add_anime import register_add_anime
from tg_bot.tg_bott.handlers.delete_anime import register_delete_anime
from tg_bot.tg_bott.handlers.view_tracked import register_view_tracked
from tg_bot.tg_bott.middleware.scheduler import SchedulerMiddleware
from tg_bott.config import load_config
# from tg_bott.handlers.echo import register_echo
from tg_bott.handlers.help import register_help_commands
from tg_bott.handlers.start import register_start

logger = logging.getLogger(__name__)
db = DataBase()


def register_middleware(dp, scheduler):
    dp.setup_middleware(SchedulerMiddleware(scheduler))


def register_filters(dp):
    pass


def register_hendler(dp):
    register_delete_anime(dp)
    register_start(dp)

    register_view_tracked(dp)
    register_add_anime(dp)

    register_help_commands(dp)
    # register_echo(dp)
    # register_ongoing(dp)


async def sounder(bot: Bot):
    conn = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(connector=conn) as session:
        parser = AParser(session=session)
        lst_of_anime = await db.select_anime()
        await parser.gather_data(lst_anime=lst_of_anime)  # Собираем новые данные об аниме
        await parser.find_new_series(lst_of_anime=lst_of_anime)  # Ищет новые серии и сипользует функц db.wrote()
    users_for_message = await db.for_sounder()

    for users, anime in users_for_message.items():
        await bot.send_message(chat_id=users, text=f'{anime["anime_name"]} вышла новая серия {anime["episodes"]} \n {anime["href"]}')
async def main():
    await db.create_table()

    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    config = load_config(path='.env')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    storage = RedisStorage2() if config.tg_bot.user_redis else MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    bot['config'] = config


    scheduler = AsyncIOScheduler()

    register_middleware(dp, scheduler)
    register_filters(dp)
    register_hendler(dp)

    scheduler.add_job(sounder, 'interval', minutes = 2, args=(bot,))

    try:
        scheduler.start()
        await dp.start_polling()


    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main=main())
    except(KeyboardInterrupt, SystemExit, RuntimeError):
        logger.error('Все кончается')
