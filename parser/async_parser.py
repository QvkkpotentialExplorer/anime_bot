import asyncio
import json
import re
import time
import aiofile
import aiohttp
from bs4 import BeautifulSoup

from typing import IO

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'
COOKIES = {
    '__ddg1_': 'XU90etO6ZpOKiHxR3kNk',
    '_ym_uid': '1675521430975046576',
    '_ym_d': '1675521430',
    '_ga': 'GA1.2.1770549851.1675521430',
    'device_view': 'full',
    '_ym_isad': '2',
    '_ym_visorc': 'b',
    '_gid': 'GA1.2.154958431.1683983697',
}
HEADERS = {
    'authority': 'animego.org',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ru,en;q=0.9',
    'referer': 'https://animego.org/anime/filter/status-is-ongoing/apply',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "YaBrowser";v="23"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.3.721 Yowser/2.5 Safari/537.36',
    'x-kl-ajax-request': 'Ajax_Request',
    'x-requested-with': 'XMLHttpRequest',
}
dict_of_anime = {}
LIST_OF_PROBLEM = [""]
PARAMS = {
    'year_from': '',
    'year_to': '',
    'genres_498562439': 'or',
    'status_4120216365': 'ongoing',
    'sort': 'createdAt',
    'direction': 'desc',
    'type': 'animes',
}


class AParser:
    def __init__(self, url: str, cookies, headers, session, params):
        self.url = url
        self.cookies = cookies
        self.headers = headers
        self.pages_count = 1
        self.session = session
        self.params = params
        self.dict_of_anime = {}

    async def max_page(self):
        """ Проходится по страничкам пока status странички не равен [endPage]

        :return page: Возвращает колличество страничек"""
        page = 0
        while True:
            page += 1
            self.params['page'] = str(page)
            async with self.session.get(url=self.url,
                                        params=self.params,
                                        cookies=self.cookies,
                                        headers=self.headers) as resp:
                resp = await resp.json()

                if resp['endPage']:
                    break
        return page

    #
    async def generate_urls(self):
        """ Формирует список urls , исходя из колличества страниче на сайте(max_page)

        :return urls: Возвращает список urls"""
        urls = []
        max_page = await self.max_page()
        for page_number in range(1,max_page+1):
            urls.append(f"{self.url}?sort=createdAt&direction=desc&type=animes&page={page_number}")
        return urls

    async def add_all_animes(self, url):
        '''
        Заполняет словарь dict_of_anime ключами (anime_name) и значением (список(ссылка на страничку аниме, None))
        :param url - ссылка на одну из 3 страниц содержащих неопределенное колличество аниме:
        '''
        async with self.session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            names_of_anime = soup.find_all('div', class_='animes-list-item media')

            # Находим ссылки непосредственно на странички самих аниме, чтобы потом узнать последнюю серию
            for item in names_of_anime:
                data_of_anime = item.find('div', class_='h5 font-weight-normal mb-1').find('a')
                # if data_of_anime.text not in LIST_OF_PROBLEM: # Расскомментируй если появятся проблемы
                self.dict_of_anime[data_of_anime.text] = f'{data_of_anime.get("href")}'

    async def get_page_data(self, url, anime_name):
        '''
        Записывает в словари dict_of_anime key : status , value : номер серии
        :param url: ссылка на одну из страничек с отдельно взятым тайтлом:
        :param anime_name: ключ в dict_of_anime
        '''
        while True:
            async with self.session.get(url) as resp:
                if resp.status != 404:
                    html = await resp.text()
                    if len(BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')) < 2:
                        await asyncio.sleep(1)
                        continue
                    print(anime_name, url)
                    self.dict_of_anime[anime_name] = {
                        "url": url,
                        "status": BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text
                    }
                    return
                else:
                    self.dict_of_anime[anime_name] = {"url": url, "status": "404"}
                    return

    async def gather_data(self):
        '''
            Сначало заполняет список tasks1 тасками с выполнением def add_all_animes .
            Следом заполняет список task2 тасками с выполнением def get_page_data
        '''
        tasks1 = []
        tasks2 = []
        for url in await self.generate_urls():
            tasks1.append(asyncio.create_task(self.add_all_animes(url=url)))
        await asyncio.gather(*tasks1)
        for anime_name, url in self.dict_of_anime.items():
            tasks2.append(asyncio.create_task(self.get_page_data(anime_name=anime_name, url=url)))
        await asyncio.gather(*tasks2)

    async def find_new_series(self):
        async with aiofile.async_open(file_specifier='data_of_series.json', mode='r', encoding='utf-8') as file:
            series_number = json.loads(await file.read())
        print(f'series_number : {series_number}')
        for anime_name in self.dict_of_anime:
            # если в json-ке нет определенного аниме , то мы добавляем его в словарик json-ки series_number

            status = self.dict_of_anime[anime_name]['status']

            if series_number.get(anime_name) is None:
                series_number[anime_name] = {"status": 0, 'status_new' : 'Nothing'}
            if series_number.get(anime_name) is None:
                print(f'{anime_name} перестало выходить в онгоинге')
            else:
                if status == 404:
                    self.dict_of_anime[anime_name]["status"] = ["0 / 0"]
                    self.dict_of_anime[anime_name]["status_new"] = ["Nothing"]

                elif re.search('[а-яА-Я]', status):

                    self.dict_of_anime[anime_name]["status"] = ["0 / 0"]
                    self.dict_of_anime[anime_name]["status_new"] = ["Nothing"]



                elif int(status.split(' / ')[0]) > series_number[anime_name]['status']:
                    print(f'{anime_name}: вышла новая серия номер {int(status.split(" / ")[0])}')
                    self.dict_of_anime[anime_name]["status_new"] = ["New"]
                else:
                    print(f'{anime_name} не вышло новой серии')
                    self.dict_of_anime[anime_name]["status_new"] = ["Nothing"]
        return self.dict_of_anime

    async def write_file(self ):
        json_dict = {}
        for anime_name, episode_number in self.dict_of_anime.items():
            print(anime_name, "::::", episode_number)
            if '/' in episode_number["status"]:
                json_dict[anime_name] = {"href": episode_number['url'],
                                         "status": int(episode_number["status"].split(' / ')[0]),
                                         "status_new": episode_number['status_new']}
        async with aiofile.async_open('data_of_series.json', mode='w', encoding='utf-8') as afp:
            data = json.dumps(json_dict, ensure_ascii=False)
            print(data)
            await afp.write(data)


async def main():
    async with aiohttp.ClientSession() as session:
        parser = AParser(url=URL, cookies=COOKIES, headers=HEADERS, session=session, params=PARAMS)
        await parser.gather_data()

        print(parser.dict_of_anime)
        await parser.find_new_series()
        await parser.write_file()
        # await parser.write_file(now_dict=parser.dict_of_anime)

        # d = await parser.g()
        # # print(parser.dict_of_anime)
        # await parser.write_file(now_dict=d)
        # await parser.find_new_series()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(end_time-start_time)