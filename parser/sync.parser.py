import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self,something):
        self.something = something

    def check(self,href):
        resp = requests.get(url=href)
        html = resp.text
        try:
            data_of_anime = BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')
            status_ongoing = data_of_anime[2].text
            anime_name = BeautifulSoup(html, 'lxml').find('div', class_='anime-title').next_element.next_element.text
            episodes = BeautifulSoup(html, 'lxml').find_all('dd', class_='col-6 col-sm-8 mb-1')[1].text
        except:
            status_ongoing="NO"

        if status_ongoing == "Онгоинг":
            return (anime_name,)
        else:
            return False

    def get_page_data(self,href):

        if self.check(href = href):
            resp = requests.get(url=href)
            html = resp.text


        return (href, anime_name, episodes,)

