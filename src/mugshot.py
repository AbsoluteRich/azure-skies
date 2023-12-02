import pygame as pg
from main import Image


class App:
    def __init__(self, name: str, image_path: str) -> None:
        self.name = name
        self.image = Image(image_path)

    def run(self):
        pg.init()
        pg.display.set_caption(self.name)
        screen = pg.display.set_mode((self.image.width, self.image.height))
        pg.display.set_icon(self.image.surface)

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            screen.blit(self.image.surface, (0, 0))
            pg.display.update()


if __name__ == '__main__':
    file_path = r""  # Insert file path here
    app = App("Have You Seen This Man?", file_path)
    app.run()
