import asyncio
import datetime

import aiohttp
from aiogram import Dispatcher
from bs4 import BeautifulSoup

from tg_bot.tg_bott.db.bot_db import DataBase

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'
cmd = {'anime': {'check': {'class': 'col-6 col-sm-8 mb-1', 'index_element': '2'}, 'get_page': {}},
       'series': {'check': {'class': "wrapper_movies_soon_episodes active", 'index_element': '0'}}}
mouths = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
          'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


class AParser:
    def __init__(self, session):
        self.session = session
        self.dict_of_anime = {}
        self.db = DataBase()

    # Это функция принимает url - ссылка на нужное аниме. И возвращает True если аниме в статусе онгинг и False если аниме не в онгоинге
    async def check(self, url, type):
        print('-----new_parser.check()------')
        async with self.session.get(url) as resp:
            html = await resp.text()
            html = BeautifulSoup(html, 'lxml')
            if type == "anime":
                try:
                    status_ongoing = html.find_all('dd', class_='col-6 col-sm-8 mb-1')[2].text

                except:
                    status_ongoing = "NO"
                return True if status_ongoing == "Онгоинг" else False
            if type == "series":
                try:
                    data_of_series = \
                        html.find('div', class_='wrapper_movies_soon_episodes active').find('div', 'active').find_all(
                            'span')[2].text.split()  # Пример : ['24', 'февраля', '2024', 'г.']
                    date_now = datetime.datetime.now()
                    if int(data_of_series[2]) >= date_now.year and mouths[
                        data_of_series[1]] >= date_now.month and int(
                        data_of_series[0]) >= date_now.day:
                        status_ongoing = "Онгоинг"
                except:
                    status_ongoing = "NO"
                return True if status_ongoing == "Онгоинг" else False

    async def get_page(self, url,type):
        if await self.check(url=url,type = type):
            if type == "anime":
                while True:
                    async with self.session.get(url=url) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html,'lxml')
                        if len(soup.find_all('dd', class_='col-6 col-sm-8 mb-1')) < 2:
                            await asyncio.sleep(1)  # Если сервер создает задержку
                            continue
                        anime_name = soup.find('div',class_='anime-title').next_element.next_element.text
                        episodes = soup.find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text
                        self.dict_of_anime[anime_name] = [url, episodes]
                        print('-----new_parser.get_page()------')
                        print(self.dict_of_anime)
                        print('-----------')
                    return anime_name, episodes,


    async def gather_data(self, lst_anime):

        for anime in lst_anime:
            await self.get_page(anime[1],type='anime')

    async def find_new_series(self, lst_of_anime,type):#lst_of_anime[[anime_name1,href1,episodes1,flag1],....]
        print('-------find_new_series-----------')
        for anime in lst_of_anime:
            anime_name = anime[2]

            if not self.dict_of_anime.get(anime_name):  # Если аниме не прошло проверку self.check()
                pass

            elif anime[4] == True:  # Меняем flag True на False после предыдущего запуска парсера
                if int(anime[3].split('/')[1]) == int(self.dict_of_anime[anime_name][1].split('/')[
                                                          0]):  # Если вышла последняя серия аниме и пользователям пришло оповещение
                    await self.db.delete_anime(anime_name=anime_name)
                else:
                    await self.db.write_on_db(episodes=self.dict_of_anime[anime_name][1], anime_name=anime_name,
                                              flag=False)


            elif int(anime[3].split('/')[0]) < int(self.dict_of_anime[anime_name][1].split('/')[
                                                       0]):  # Если количество серий , спаршеных с сайта больше количества серий,взятых с бд
                await self.db.write_on_db(episodes=self.dict_of_anime[anime_name][1], anime_name=anime_name, flag=True)
                print(f'{anime_name} flag = True')
            else:
                pass


async def main():
    async with aiohttp.ClientSession() as session:
        parser = AParser(session=session)
        await parser.check(url="https://www.film.ru/movies/tri-mushketyora-miledi", type="series")


if __name__ == "__main__":
    asyncio.run(main())
