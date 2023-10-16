import asyncio
import json
import re

import aiofile
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'

dict_of_anime = {}
# словарь ключ(anime_name) и значения в виде списка(url, last_episode,new/last)
list_of_problem = [""]
cookies = {
    '__ddg1_': 'XU90etO6ZpOKiHxR3kNk',
    '_ym_uid': '1675521430975046576',
    '_ym_d': '1675521430',
    '_ga': 'GA1.2.1770549851.1675521430',
    'device_view': 'full',
    '_ym_isad': '2',
    '_ym_visorc': 'b',
    '_gid': 'GA1.2.154958431.1683983697',
}
headers = {
    'authority': 'animego.org',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ru,en;q=0.9',
    # 'cookie': '__ddg1_=XU90etO6ZpOKiHxR3kNk; _ym_uid=1675521430975046576; _ym_d=1675521430; _ga=GA1.2.1770549851.1675521430; device_view=full; _ym_isad=2; _ym_visorc=b; _gid=GA1.2.154958431.1683983697',
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


async def add_all_animes(url, session: ClientSession):
    '''
    Заполняет словарь dict_of_anime ключами (anime_name) и значением (список(ссылка на страничку аниме, None))
    :param url - ссылка на одну из 3 страниц содержащих неопределенное колличество аниме:
    :param session:
    :return dict_of_anime:
    '''
    # Находим название с одной странички
    async with session.get(url) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
        names_of_anime = soup.find_all('div', class_='animes-list-item media')
    # Находим ссылки непосредственно на странички самих аниме,чтобы потом узнать последнюю серию
    for item in names_of_anime:
        data_of_anime = item.find('div', class_='h5 font-weight-normal mb-1').find('a')
        if data_of_anime.text in list_of_problem:
            pass
        else:
            dict_of_anime[data_of_anime.text] = (f'{data_of_anime.get("href")}', None)


async def final_add(session) -> dict:
    '''
    Заполняет словарь dict_of_anime ключами (anime_name) и значениями (спиксок(ссылка на страничку аниме,последняя серия))
    :param session:
    :return dict_of_anime:
    '''
    print(dict_of_anime)
    # Ищем через url(url[0] - это как раз наша href ) gjcktly.. cthb. fybvt
    for anime_name, url in dict_of_anime.items():
        print(anime_name, url[0])
        async with session.get(url[0]) as resp:
            if resp.status != 404:
                html = await resp.text()
                soup = BeautifulSoup(html, 'lxml')
                dict_of_anime[anime_name] = [url[0], (soup.find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text)]
            else:
                dict_of_anime[anime_name] = [url[0], 404]
    print(dict_of_anime)
    return dict_of_anime


async def find_new_series(episodes: dict):
    '''

    :param episodes (наш словарик dict_of_anime):
    :return:
    '''
    async with aiofile.async_open(file_specifier='data_of_series.json', mode='r', encoding='utf-8') as file:
        series_number = {}
        new_series = {}
        for anime_name, episode_number in json.loads(await file.read()).items():
            series_number[anime_name] = episode_number
    print(f'series_number : {series_number}')
    for anime_name, episode_number in episodes.items():
        # если в json-ке нет определенного аниме , то мы добавляем его в словарик json-ки series_number
        print(episode_number[1])
        if series_number.get(anime_name) is None:
            series_number[anime_name] = [0]
        if series_number.get(anime_name)[0] is None:
            print(f'{anime_name} перестало выходить в онгоинге')
        else:
            if episode_number[1] == 404:
                episode_number[1] = "0 / 0"
                episode_number.append("Nothing")

            elif re.search('[а-яА-Я]', episode_number[1]):

                episode_number[1] = "0 / 0"
                episode_number.append("Nothing")



            elif int(episode_number[1].split(' / ')[0]) > series_number.get(anime_name)[0]:
                print(f'{anime_name}: вышла новая серия номер {int(episode_number[1].split(" / ")[0])}')
                episode_number.append('New')
            else:
                print(f'{anime_name} не вышло новой серии')
                episode_number.append('Nothing')
    return episodes


async def write_file(now_dict):
    json_dict = {}
    for anime_name, episode_number in now_dict.items():
        if '/' in episode_number[1]:
            json_dict[anime_name] = (int(episode_number[1].split(' / ')[0]), episode_number[2])
    with open('data_of_series.json', 'w', encoding='utf-8') as afp:
        json.dump(json_dict, afp)


async def max_page():
    '''
    Ищет сколько всего страниц с онгоинагми
    :return page:
    '''
    async with aiohttp.ClientSession() as session:
        page: int = 0
        while True:
            page += 1
            params = {
                'year_from': '',
                'year_to': '',
                'genres_498562439': 'or',
                'status_4120216365': 'ongoing',
                'sort': 'createdAt',
                'direction': 'desc',
                'type': 'animes',
                'page': str(page),
            }
            async with session.get(URL,
                                   params=params,
                                   cookies=cookies,
                                   headers=headers) as resp:
                r = await resp.json()
                if r['endPage']:
                    break
    print(page)
    return page


async def main():
    tasks = []
    # Ищем количество страничек
    mx_pg = await asyncio.create_task(max_page())

    async with aiohttp.ClientSession() as session:
        for now_page in range(1, max(mx_pg+1, 2)):
            tasks.append(asyncio.create_task(add_all_animes(url=f"{URL}?sort=createdAt&direction=desc&type=animes&page={now_page}", session=session))),
        await asyncio.gather(*tasks)
        # Добавляем в наш список dict_of_anime номер последней серии
        long_task = asyncio.create_task(final_add(session=session))

        await long_task
        # result= await long_task
        # print(result)

        finally_result = asyncio.create_task(find_new_series(episodes=dict_of_anime))
        result = await finally_result
        print(result)

        file_task = asyncio.create_task(write_file(now_dict=result))
        await file_task


asyncio.run(main())
print(dict_of_anime)
print("--------------------")


def get_anime(url, dict_of_anime):
    for anime_name, url1 in dict_of_anime.items():
        if str(url1[0]) == str(url):
            print(anime_name)
            break

print(len(dict_of_anime))
get_anime(url='https://animego.org/anime/zvezdnoe-ditya-2307', dict_of_anime=dict_of_anime)
