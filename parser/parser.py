import asyncio
import datetime
import json
import re
import time
import aiofile
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

URL = 'https://animego.org/anime/filter/status-is-ongoing/apply'


async def get_serial_data(href):
    async with aiohttp.ClientSession() as session:
        html = await session.get(href)
        html = await html.text()
        soup = BeautifulSoup(html,'lxml')
        name_of_series = soup.find_all('h1')
        count_series = soup.find('div', class_ = "wrapper_movies_soon_episodes active")
        print(count_series.find_all('span')[2].text.split())
        print(name_of_series[0].text)
async def main():
    await get_serial_data("https://www.film.ru/serials/mese-speyd#soon")

if __name__ == "__main__":
    asyncio.run(main())

print(datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day)