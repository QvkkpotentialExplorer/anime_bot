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
        self.dict_of_titles = {'anime':{},'series':{}}
        self.db = DataBase()

    # Это функция принимает url - ссылка на нужное аниме. И возвращает True если аниме в статусе онгинг и False если аниме не в онгоинге
    async def check(self, url, content_type):
        print('-----new_parser.check()------')
        async with self.session.get(url) as resp:
            html = await resp.text()
            html = BeautifulSoup(html, 'lxml')
            if content_type == "anime":
                print("аниме")
                try:
                    status_ongoing = html.find_all('dd', class_='col-6 col-sm-8 mb-1')[2].text
                    return True
                except:
                    return False

            if content_type == "series":
                try:
                    data_of_series = \
                        html.find('div', class_='wrapper_movies_soon_episodes active').find('div', 'active').find_all(
                            'span')[2].text.split()  # Пример : ['24', 'февраля', '2024', 'г.']
                    date_now = datetime.datetime.now()
                    if int(data_of_series[2]) >= date_now.year and mouths[
                        data_of_series[1]] >= date_now.month and int(
                        data_of_series[0]) >= date_now.day:
                        return True
                except:
                    return False

    async def get_page(self, url,content_type):
        print('-----new_parser.get_page()------')
        if await self.check(url=url,content_type=content_type):
            if content_type == "anime":
                while True:
                    async with self.session.get(url=url) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html,'lxml')
                        if len(soup.find_all('dd', class_='col-6 col-sm-8 mb-1')) < 2:
                            await asyncio.sleep(1)  # Если сервер создает задержку
                            continue
                        title_name = soup.find('div',class_='anime-title').next_element.next_element.text
                        episodes = soup.find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text
                        self.dict_of_titles[content_type][title_name] = [url, episodes]

                        print(self.dict_of_titles[content_type])
                        print('-----------')
                    return title_name, episodes,
            if content_type == "series":
                while True:
                    async with self.session.get(url=url) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'lxml')
                        title_name = soup.find('h2').text
                        episodes = soup.find('div', class_ = "wrapper_movies_soon_episodes active").find_all('div',class_ = "active")[-1]
                        episodes = episodes.next_element.text.split()[0]

                        self.dict_of_titles[content_type][title_name] = [url, episodes]
                        print('-----new_parser.get_page()------')
                        print(episodes)
                        print('-----------')
                    return title_name, episodes,


    async def gather_data(self, lst_anime,lst_series):
        for series in lst_series:
            await self.get_page(series[1], content_type='series')
        for anime in lst_anime:
            await self.get_page(anime[1],content_type='anime')

    async def find_new_series(self, lst_of_anime,lst_of_series):#lst_of_anime[[anime_name1,href1,episodes1,flag1],....]
        print('-------find_new_series-----------')
        content_type = 'anime'
        for anime in lst_of_anime:
            print(lst_of_anime)
            anime_name = anime[2]
            now_episode = self.dict_of_titles[content_type][anime_name][1].split('/')[0]
            print(now_episode)
            print(anime[4])
            if not self.dict_of_titles[content_type].get(anime_name):  # Если аниме не прошло проверку self.check()
                pass

            elif anime[4] == True:  # Меняем flag True на False после предыдущего запуска парсера
                if not '?' in anime[3].split('/')[1] :
                    if int(anime[3].split('/')[1]) == int(now_episode):  # Если вышла последняя серия аниме и пользователям пришло оповещение
                        await self.db.delete_anime(anime_name=anime_name)
                await self.db.write_on_db(episodes=self.dict_of_titles[content_type][anime_name][1], name=anime_name,
                                              flag=False,content_type=content_type)


            elif int(anime[3].split('/')[0]) < int(now_episode):  # Если количество серий , спаршеных с сайта больше количества серий,взятых с бд
                await self.db.write_on_db(episodes=self.dict_of_titles[content_type][anime_name][1], name=anime_name, flag=True,content_type=content_type)
                print(f'{anime_name} flag = True')
            else:
                pass
        for series in lst_of_series:
            content_type = 'series'
            series_name = series[2]
            now_episode = series[3]
            if not self.dict_of_titles[content_type].get(series_name):  # Если аниме не прошло проверку self.check()
                pass

            elif series[4] == True:  # Меняем flag True на False после предыдущего запуска парсера
                await self.db.write_on_db(episodes=self.dict_of_titles[content_type][series_name][1], name=series_name,
                                          flag=False,content_type=content_type)


            elif int(series[3]) < int(self.dict_of_titles[content_type][series_name][1]):  # Если количество серий , спаршеных с сайта больше количества серий,взятых с бд
                await self.db.write_on_db(episodes=self.dict_of_titles[content_type][series_name][1], name=series_name, flag=True,content_type=content_type)
                print(f'{series_name} flag = True')
            else:
                pass


async def main():
    async with aiohttp.ClientSession() as session:
        parser = AParser(session=session)
        await parser.check(url="https://www.film.ru/movies/tri-mushketyora-miledi", content_type="series")


if __name__ == "__main__":
    asyncio.run(main())
