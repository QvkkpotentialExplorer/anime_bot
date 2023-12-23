import asyncio

import aiohttp
from bs4 import BeautifulSoup

from tg_bot.tg_bott.db.bot_db import DataBase

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'


class AParser:
    def __init__(self, session):
        self.session = session
        self.dict_of_anime = {}
        self.db = DataBase()

    # Это функция принимает url - ссылка на нужное аниме. И возвращает True если аниме в статусе онгинг и False если аниме не в онгоинге
    async def check(self, url):
        async with self.session.get(url) as resp:
            html = await resp.text()
            try:
                data_of_anime = BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')
                status_ongoing = data_of_anime[2].text
            except:
                status_ongoing = "NO"
            return True if status_ongoing == "Онгоинг" else False

    async def get_page(self, url):
        if await self.check(url=url):
            while True:
                async with self.session.get(url=url) as resp:
                    html = await resp.text()
                    if len(BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')) < 2:
                        await asyncio.sleep(1)  # Если сервер создает задержку
                        continue
                    anime_name = BeautifulSoup(html, 'lxml').find('div',
                                                                  class_='anime-title').next_element.next_element.text
                    episodes = BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text
                    self.dict_of_anime[anime_name] = [url, episodes]
                    print('-----new_parser.gep_page()------')
                    print(self.dict_of_anime)
                    print('-----------')
                return anime_name, episodes,
        else:
            return False

    async def gather_data(self, lst_anime):

        for anime in lst_anime:
            await self.get_page(anime[1])

    async def find_new_series(self, lst_of_anime):

        for anime in lst_of_anime:
            anime_name = anime[2]

            if not self.dict_of_anime.get(anime_name):  # Если аниме не прошло проверку self.check()
                pass

            elif int(anime[3].split('/')[0]) < int(self.dict_of_anime[anime_name][1].split('/')[0]):
                await self.db.write_on_db(episodes=self.dict_of_anime[1], anime_name=anime_name, flag=True)
                print(f'{anime_name} flag = True')
            else:
                pass
