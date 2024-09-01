from scraper.Scraper import Scraper


class GameEnv(Scraper):
    def __init__(self, url="https://play2048.co/", n_field=16):
        super().__init__(url, n_field)
        print(self.matrix)

        self.play_game()
    def play_game(self):
        while True:
            # keyboard.on_press(lambda e: print(e.name))
            if self.check_game_is_over():
                result = 0
            self.move()
            self.get_html()
            print(self.matrix)
            print(self.result)


x = GameEnv()
