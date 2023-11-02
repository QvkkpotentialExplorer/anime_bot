import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def check(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            try:
                soup = BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')[2].text
            except:
                soup = ""
    if soup == "Онгоинг":
        return True
    else:
        return False
