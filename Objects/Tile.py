class TitleElement:
    def __init__(self, value, position, status=False):
        self.value = int(value.replace("tile-","")) if value else None
        self.position = position.replace("tile-position-", "").split("-") if position else None
        self.position = [int(i) for i in self.position]
        self.merged = True if status == "title-new" else False

    def __repr__(self):
        return f'{self.value}'

    def __str__(self):
        return f'{self.value}'
