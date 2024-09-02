import time

from mover.Mover import Mover
from scraper.Scraper import Scraper
from trainer.Trainer import Trainer


class GameEnv(Trainer):
    def __init__(self, url="https://play2048.co/", n_field=16):
        super().__init__(url, n_field)
        self.play_game()

    def play_game(self):
        while True:
            self.start()


x = GameEnv()
