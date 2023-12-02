import pygame as pg
from main import Sprite, window_width, window_height


def get_centre(surface) -> tuple[int, int]:
    # https://pastebin.com/diqQBz4Y
    width, height = pg.display.get_window_size()
    centre = (width // 2 - surface.get_width() // 2), (height // 2 - surface.get_height() // 2)
    return centre


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((window_width, window_height))
    """
    player = Sprite("spaceship.png", 0, 0)
    player_centre = get_centre(player.image.surface)
    print(player_centre)
    """
    font = pg.font.Font("Neuropolitical.otf", 30)
    game_over_text = font.render(f"Game Over!", True, (255, 0, 0))
    print(get_centre(game_over_text))
