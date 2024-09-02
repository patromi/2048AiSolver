import math

import numpy as np
from bs4 import BeautifulSoup


class ScraperUtils:
    def __init__(self, url: str, n_field: int):
        self.in_row = self._get_in_row(n_field=n_field)
        self.url = url

    @staticmethod
    def _calc_result(result: str):
        if result:
            result = result.split('+')
            return int(result[0])

    def _get_empty_matrix(self):
        return np.zeros((self.in_row, self.in_row))

    @staticmethod
    def _get_in_row(n_field: int):
        return round(math.sqrt(n_field))
