import pygame as pg
from random import randint
import os


class Image:
    def __init__(self, path: str):
        self.path = path
        self.surface = pg.image.load(self.path)
        self.rect = self.surface.get_rect()
        self.width, self.height = self.surface.get_size()


class Sprite:
    def __init__(self, image_path: str, x: int | float, y: int | float, **kwargs: any):
        self.image = Image(image_path)
        self.x = x
        self.y = y
        self.direction = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.state = kwargs  # Used for miscellaneous, sprite-specific info

    def draw(self, display: pg.Surface) -> None:
        display.blit(self.image.surface, (self.x, self.y))

    def move(self, amount: int | float) -> None:
        if self.direction["left"] and self.direction["right"]:
            pass
        elif self.direction["left"]:
            self.x += -amount
        elif self.direction["right"]:
            self.x += amount

        if self.direction["up"] and self.direction["down"]:
            pass
        elif self.direction["up"]:
            self.y += -amount
        elif self.direction["down"]:
            self.y += amount


# Global variables
window_height = 500
window_width = 750
fps = 60

if __name__ == '__main__':
    working_directory = os.getcwd()
    potential_paths = [
        os.path.join(working_directory, "assets"),  # /project/assets from /project/ (used in prod)
        os.path.join(os.path.split(os.getcwd())[0], "assets")  # /project/assets/ from /project/src/ (used in dev)
    ]

    for file_path in potential_paths:
        if os.path.exists(file_path):
            os.chdir(file_path)
            break
    else:
        raise FileNotFoundError("Assets directory not found")

    pg.init()

    # Local variables
    running = True
    speed = 8
    score = 0
    enemy_count = 6
    font = pg.font.Font("Neuropolitical.otf", 30)
    game_over = False

    # Setting up the window
    screen = pg.display.set_mode((window_width, window_height), pg.RESIZABLE)
    pg.display.set_caption("Azure Skies")  # Working name
    pg.display.set_icon(pg.image.load("icon.png"))
    clock = pg.time.Clock()

    # Sprites
    player = Sprite("spaceship.png", 343, 218 + 200)
    enemies = []
    background = Sprite("background.png", 0, 0)
    laser = Sprite("laser.png", 0, player.y, visible=False, activated=False)

    # Adding multiple enemies
    for _ in range(enemy_count):
        enemy = Sprite("ufo.png", 343, 218 - 200)

        # Setting up their attributes
        enemy.x = randint(0, window_width - enemy.image.width)
        enemy.y = randint(enemy.y, enemy.y + 200)
        if randint(1, 2) == 1:
            enemy.direction["left"] = True
        else:
            enemy.direction["right"] = True

        enemies.append(enemy)

    # Ear hurting (audio)
    pg.mixer.music.load("mus_earth.wav")
    pg.mixer.music.play(-1)
    laser_sfx = pg.mixer.Sound("sfx_laser.wav")
    enemy_explosion_sfx = pg.mixer.Sound("sfx_enemy_explosion.wav")
    player_explosion_sfx = pg.mixer.Sound("sfx_player_explosion.wav")

    while running:
        # Runs the game loop 60 times per second (frame rate)
        clock.tick(fps)

        # ================================= INPUT =================================
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = False

                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_LEFT:
                            player.direction["left"] = True
                        case pg.K_RIGHT:
                            player.direction["right"] = True
                        case pg.K_z:
                            if not laser.state["visible"]:
                                laser.state["activated"] = True

                case pg.KEYUP:
                    match event.key:
                        case pg.K_LEFT:
                            player.direction["left"] = False
                        case pg.K_RIGHT:
                            player.direction["right"] = False

        # ================================= UPDATE =================================
        if not game_over:
            # Sprite movements
            player.move(speed)
            for enemy in enemies:
                enemy.move(speed * 0.5)

                # Enemy goes past the player
                # ChatGPT wrote this condition
                if enemy.y + enemy.image.height >= player.y:
                    player_explosion_sfx.play()
                    game_over = True

            # Constraining the player's movement
            if player.x <= 0:
                player.x = 0
            elif player.x >= window_width - player.image.width:
                # Accounting for the size of the sprite, since Pygame starts drawing images from the left
                player.x = window_width - player.image.width

            # Teleporting the enemy
            for enemy in enemies:
                if enemy.x <= 0 or enemy.x >= window_width - enemy.image.width:
                    enemy.direction["left"] = not enemy.direction["left"]  # TIL you could do this, thanks, ChatGPT
                    enemy.direction["right"] = not enemy.direction["right"]
                    enemy.y += speed * 6

            # Projectile logic & movement
            if laser.state["activated"]:
                laser.state["activated"] = False
                laser.state["visible"] = True
                laser.x = player.x + 16
                laser.y = player.y - 32
                laser_sfx.play()

            if laser.state["visible"]:
                laser.direction["up"] = True
                laser.move(speed * 2)

                if laser.y <= (0 - laser.image.height):  # Wait until the bullet fully goes off the screen
                    laser.x = player.x + 16
                    laser.y = player.y - 32
                    laser.state["visible"] = False

            # Laser vs alien
            for enemy in enemies:
                if laser.state["visible"]:
                    # Otherwise the enemy will collide with the laser and teleport to the top, since it starts just
                    # above the player
                    enemy_rectangle = enemy.image.surface.get_rect(x=enemy.x, y=enemy.y)
                    laser_rectangle = laser.image.surface.get_rect(x=laser.x, y=laser.y)
                    if enemy_rectangle.colliderect(laser_rectangle):
                        # Clean up the bullet
                        laser.x = player.x + 16
                        laser.y = player.y - 32
                        laser.state["visible"] = False

                        # Clean up the enemy
                        enemy.y = 218 - 200
                        enemy.x = randint(0, window_width - enemy.image.width)

                        # Audiovisual feedback
                        score += 1
                        enemy_explosion_sfx.play()

        # HUD
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))

        current_fps = clock.get_fps()
        if current_fps >= (fps - 10):  # Is this what bad FPS is?
            fps_text = font.render(f"FPS: {current_fps:.0f}", True, (255, 255, 255))
        else:
            fps_text = font.render(f"FPS: {current_fps:.0f}", True, (255, 0, 0))

        game_over_text = font.render(f"Game Over!", True, (255, 255, 255))

        # ================================= RENDER =================================
        # Drawing all the graphics
        screen.fill((20, 35, 80))
        background.draw(screen)

        screen.blit(score_text, (10, 10))
        screen.blit(fps_text, (window_width - 170, 10))

        player.draw(screen)

        if not game_over:
            for enemy in enemies:
                enemy.draw(screen)

            if laser.state["visible"]:
                laser.draw(screen)
        else:
            screen.blit(game_over_text, (266, 232))

        pg.display.update()

    pg.quit()
