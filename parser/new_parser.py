import asyncio

from bs4 import BeautifulSoup

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'


class AParser:
    def __init__(self, session):
        self.session = session
        self.dict_of_anime = {}

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
                return url, anime_name, episodes,
        else:
            return False
