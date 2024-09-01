import random

from bs4 import BeautifulSoup
import numpy as np
import math
from selenium import webdriver
from selenium.webdriver import ActionChains
from Objects.Tile import TitleElement
from selenium.webdriver.common.keys import Keys

class Scraper:
    def __init__(self, url: str, n_field: int):
        self.in_row = self._get_in_row(n_field=n_field)
        self.browser = webdriver.Firefox()
        self.result = 0
        self.matrix = self._get_empty_matrix()
        self._open_url(url=url)
        self.allowed_keybinds = ('w', 's', 'd', 'a')

    def _get_empty_matrix(self):
        return np.zeros((self.in_row, self.in_row))

    @staticmethod
    def _get_in_row(n_field : int):
        return round(math.sqrt(n_field))

    def _open_url(self,url:str):
        self.browser.get(url)

    def get_html(self):
        if self.browser.title != '2048':
            raise InterruptedError("Website is not loaded correctly")
        html = self.browser.page_source
        assert '2048' in self.browser.title
        return self.parse_html(html)

    def _calc_result(self, result: str):
        if result:
            result = result.split('+')
            return sum([int(i) for i in result])

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.find('div', {'class': 'score-container'}).text
        self.result = result if result.isdigit() else self._calc_result(result)
        game_field = soup.find('div', {'class': 'tile-container'})
        tile_elements = []
        for tile_html in game_field.children:
            if len(tile_html.get("class")) == 3:
                _, name, position = tile_html.get("class")
                tile_elements.append(TitleElement(name, position, None))
            else:
                _, name, position, status = tile_html.get("class")
                tile_elements.append(TitleElement(name, position, status))
        self.update_matrix(tile_elements)

    def update_matrix(self, square_elements: list[TitleElement]):
        self.matrix = np.zeros((self.in_row, self.in_row))
        for square in square_elements:
            self.matrix[square.position[1] - 1][square.position[0] - 1] = square.value

    def check_game_is_over(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div", {"class": "game-message game-over"})
        if div is not None:
            retry_btn = self.browser.find_element('class name','retry-button')
            ActionChains(self.browser).click(retry_btn).perform()

    def move(self):
        number = random.randint(0, 3)
        key = self.allowed_keybinds[number]

        # Mapowanie klawiszy na odpowiednie kody klawiszy JavaScript
        key_map = {
            "up": "ArrowUp",
            "down": "ArrowDown",
            "left": "ArrowLeft",
            "right": "ArrowRight",
            "w": "KeyW",
            "a": "KeyA",
            "s": "KeyS",
            "d": "KeyD"
        }

        # Sprawdzenie, czy klucz istnieje w mapie
        if key in key_map:
            js_code = f'''
            var event = new KeyboardEvent('keydown', {{
                key: '{key_map[key]}',
                code: '{key_map[key]}',
                keyCode: {ord(key_map[key][-1])}, 
                which: {ord(key_map[key][-1])}, 
                bubbles: true 
            }});
            document.dispatchEvent(event);
            '''
            self.browser.execute_script(js_code)

