import time

from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver
from selenium.webdriver import ActionChains
from Objects.Tile import TitleElement
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from mover.Mover import Mover
from .utils import ScraperUtils


class Scraper(ScraperUtils, Mover):
    def __init__(self, url: str, n_field: int):
        super().__init__(url, n_field)
        firefox_options = Options()
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_capability("unhandledPromptBehavior", "ignore")

        capabilities = DesiredCapabilities().FIREFOX
        capabilities["unhandledPromptBehavior"] = "ignore"
        self.browser = webdriver.Firefox(options=firefox_options)

        self.result = 0
        self.matrix = self._get_empty_matrix()
        self._open_url(url=url)

    def make_action(self, action):
        self.move(action)
        self.get_html()
        return self.matrix, self.result

    def reset(self):
        print("Resetting the game")
        new_btn = self.browser.find_element('class name', 'restart-button')
        ActionChains(self.browser).click(new_btn).perform()
        self.get_html()
        return self.matrix

    def get_html(self):
        if self.browser.title != '2048':
            raise InterruptedError("Website is not loaded correctly")
        html = self.browser.page_source
        assert '2048' in self.browser.title
        return self.parse_html(html)

    def _open_url(self, url: str):
        self.browser.get(url)

    def scrap_result(self, soup: BeautifulSoup):
        result = soup.find('div', {'class': 'score-container'}).text
        self.result = int(result) if result.isdigit() else self._calc_result(result)

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        self.scrap_result(soup)

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
        self.get_html()
        if 0 in self.matrix:
            return False
        for i in range(self.in_row):
            for j in range(self.in_row):
                if j + 1 < self.in_row and self.matrix[i][j] == self.matrix[i][j + 1]:
                    return False
                if i + 1 < self.in_row and self.matrix[i][j] == self.matrix[i + 1][j]:
                    return False

        # retry_btn = self.browser.find_element('class name', 'retry-button')

        # ActionChains(self.browser).click(retry_btn).perform()
        time.sleep(1)
        print(self.matrix)
        print("Game is over")
        return True