import os
import random
import sys

import pygame_menu as pg_m
import pygame as pg

GESTURE_MODE = False

if GESTURE_MODE:
    try:
        from gesture import Gesture
    except Exception as import_error:
        Gesture = None
        print(f"Gesture module disabled: {import_error}")

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

CHARACTER_WIDTH = 300
CHARACTER_HEIGHT = 375

FPS = 60

font = pg.font.Font(None, 40)
big_font = pg.font.Font(None, 80)


def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text):
    return font.render(str(text), True, "black")


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()

        self.folder = folder
        self.load_animations()

        self.hp = 200
        self.max_hp = 200

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.charge_power = 0

    def load_animations(self):
        self.idle_animation_right = [
            load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
            for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [
            load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
            for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

        self.fireballs = pg.sprite.Group()

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()

    def handle_attack_mode(self, player):
        if not self.attack_mode:
            attack_probability = 1

            if player.charge_mode:
                attack_probability += 2

            if random.randint(1, 100) <= attack_probability:
                self.attack_mode = True
                self.charge_power = random.randint(1, 100)

                if player.rect.centerx < self.rect.centerx:
                    self.side = "left"
                else:
                    self.side = "right"

                self.animation_mode = False
                self.image = self.attack[self.side != "right"]

        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.fireballs.add(Magicball(fireball_position, self.side, self.charge_power, folder=self.folder))
            self.charge_power = 0

            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()

    def handle_movement(self):
        if self.attack_mode:
            return

        now = pg.time.get_ticks()

        if now - self.move_timer < self.move_duration:
            self.animation_mode = True
            self.rect.x += self.direction
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1, 100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400, 1500)
                self.direction = random.choice([-1, 1])
            else:
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

    def handle_animation(self):
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()


class Player(pg.sprite.Sprite):
    def __init__(self,first_player = True):
        super().__init__()

        folder = "fire wizard"
        self.folder = folder
        self.load_animations()

        if first_player:
            self.coord = (100, SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_right
            self.side = "right"

            self.key_right = pg.K_d
            self.key_left = pg.K_a
            self.key_down = pg.K_s
            self.key_charge = pg.K_SPACE

        else:
            self.coord = (SCREEN_WIDTH - 100 , SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_left
            self.side = 'left'

            self.key_right = pg.K_RIGHT
            self.key_left = pg.K_LEFT
            self.key_down = pg.K_DOWN
            self.key_charge = pg.K_RCTRL



        self.hp = 200
        self.max_hp = 200

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_right

        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.animation_mode = True

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")

        self.charge_mode = False

        self.attack_mode = False
        self.attack_interval = 500

    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/fire wizard/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

        self.down_anim = [load_image(f"images/{self.folder}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down_anim.append(pg.transform.flip(self.down_anim[0], True, False))

        self.fireballs = pg.sprite.Group()

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    def handle_movement(self, direction, keys, gesture):
        if self.attack_mode:
            return

        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            self.current_animation = (self.move_animation_left if direction == -1 else self.move_animation_right)
        elif keys[self.key_down]:
            self.animation_mode = False
            self.charge_mode = False
            self.image = self.down[self.side != "right"]
        elif (GESTURE_MODE and gesture == "live long") or (not GESTURE_MODE and keys[self.key_charge]):
            self.animation_mode = False
            self.image = self.charge[self.side != "right"]
            self.charge_mode = True
        else:
            self.animation_mode = True
            self.charge_mode = False
            self.current_animation = (self.idle_animation_left if self.side == "left" else self.idle_animation_right)

    def update(self, gesture):
        keys = pg.key.get_pressed()
        direction = 0

        if keys[pg.K_left]:
            direction = -1
            self.side = "left"

        elif keys[pg.K_right]:
            direction = 1
            self.side = "right"

        self.handle_animation()
        self.handle_movement(direction, keys, gesture)
        self.handle_attack_mode()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True

        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("red")
            if self.charge_power == 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.fireballs.add(Magicball(fireball_position, self.side, self.charge_power, folder=f"{self.folder}"))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()


class Magicball(pg.sprite.Sprite):
    def __init__(self, coord, side, power, folder):
        super().__init__()

        self.side = side
        self.power = power

        self.image = load_image(f"images/{folder}/magicball.png", 200, 150)
        if self.side == "right":
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()

        self.rect.center = coord[0], coord[1] + 120

    def update(self):
        if self.side == "right":
            self.rect.x += 4
        elif self.side == "left":
            self.rect.x -= 4

        if self.rect.x >= SCREEN_WIDTH:
            self.kill()

        elif self.rect.x <= 0:
            self.kill()


class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((900, 500))
        self.menu = pg_m.Menu(
            height=500,
            width=900,
            theme=pg_m.themes.THEME_DARK,
            title="главное меню"
        )
        # self.menu.add.text_input("Ваше имя:  ", default='Игрок', onchange=self.set_name)
        self.menu.add.label(title="Режим для одного ")
        self.menu.add.selector("Противник:   ", [('Маг земли', 1), ('error_Y_nub', 2)])
        self.menu.add.button("Играть", self.start_game)
        self.menu.add.label(title="Режим для двух")
        self.menu.add.selector("Игрок 1:   ", [('Маг земли', 1), ('error_Y_nub', 2)])
        self.menu.add.selector("Игрок 2:   ", [('Маг земли', 1), ('error_Y_nub', 2)])
        self.menu.add.button("Играть", self.start_game)
        self.menu.add.button("Выйти", self.quit_game)

        self.enemies = ["lightning wizard", "earth monk"]
        self.enemy = None

        self.enemies = ["lightning wizard", "earth monk"]
        self.enemy = self.enemies[0]

        # Эти три строки — новые. Они нужны для хранения информации, кто за кого играет
        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[0]
        self.right_player = self.players[0]

        self.run()

        self.run()

    def set_enemy(self, selected, value):
        if value in (1, 2):
            self.enemy = self.enemies[value - 1]
        else:
            self.enemy = random.choice(self.enemies)

    def set_left_player(self, selected, value):
        self.left_player = self.players[value - 1]

    def set_right_player(self, selected, value):
        self.right_player = self.players[value - 1]

    def start_one_player_game(self):
        Game("one player", (self.enemy,))

    def start_two_player_game(self):
        Game("two players", (self.left_player, self.right_player))

    def run(self):
        self.menu.mainloop(self.surface)

    def start_game(self):
        Game()

    def quit_game(self):
        quit()

    def run(self):
        self.menu.mainloop(self.surface)

class Game:
    def __init__(self, mode, wire_wizar):

        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frontground = load_image("images/front_ground.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player = Player()
        self.enemy = Enemy(folder="earth monk")

        self.clock = pg.time.Clock()

        self.gesture = None

        self.game_over = False
        self.winner = None

        global GESTURE_MODE

        if self.mode == "one player":
            if GESTURE_MODE:
                print("Загрузка модуля жестов...")
                self.g = Gesture()
                print("Загрузка завершена")

                self.GET_GESTURE = pg.USEREVENT + 1
                pg.time.set_timer(self.GET_GESTURE, 1000)
        else:
            GESTURE_MODE = False

        self.is_running = True
        self.run()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

            if GESTURE_MODE:
                if event.type == self.GET_GESTURE:
                    self.gesture = self.g.get_gesture()

            if event.type == pg.KEYDOWN and self.win is not None :
                self.is_running = False



    def run(self):
        while True:
            self.event()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(FPS)


    def update(self):
        if self.winner is None:
            if self.player.hp <= 0:
                self.game_over = True
                self.winner = "enemy"
                return

            if self.enemy.hp <= 0:
                self.game_over = True
                self.winner = "player"
                return

            self.player.update(self.gesture)
            self.player.fireballs.update()

            self.enemy.update(self.player)
            self.enemy.fireballs.update()

            hits = pg.sprite.spritecollide(self.enemy, self.player.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
            for hit in hits:
                self.enemy.hp -= hit.power

                if self.enemy.hp < 0:
                    self.enemy.hp = 0
                print(f"Enemy HP: {self.enemy.hp}")
            if self.enemy.image not in self.enemy.down_anim:
                hits = pg.sprite.spritecollide(self.enemy, self.player.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
                for hit in hits:
                    self.player.hp -= hit.power

            if self.player.image not in self.player.down_anim:
                hits = pg.sprite.spritecollide(self.player, self.enemy.fireballs, True, pg.sprite.collide_rect_ratio(0.3))
                for hit in hits:
                    self.player.hp -= hit.power
                    if self.player.hp < 0:
                        self.player.hp = 0
                print(f"Player HP: {self.player.hp}")

    def draw(self):

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.enemy.image, self.enemy.rect)

        if self.mode == "two players":
            if self.enemy.charge_mode:
                self.screen.blit(self.enemy.charge_indicator, (self.enemy.rect.left + 120, self.enemy.rect.top))

        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator, (self.player.rect.left + 120, self.player.rect.top))

        self.player.fireballs.draw(self.screen)
        self.enemy.magic_balls.draw(self.screen)

        self.screen.blit(text_render(self.gesture), (0, 0))

        bar_width = 100
        bar_height = 12
        bar_x = self.player.rect.centerx - bar_width // 2
        bar_y = self.player.rect.top - 20

        pg.draw.rect(self.screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

        health_ratio = self.player.hp / self.player.max_hp
        health_width = int(bar_width * health_ratio)
        pg.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

        hp_text = font.render(f"{self.player.hp}/{self.player.max_hp}", True, (0, 0, 0))
        self.screen.blit(hp_text, (bar_x, bar_y - 25))

        bar_x_enemy = self.enemy.rect.centerx - bar_width // 2
        bar_y_enemy = self.enemy.rect.top - 20

        pg.draw.rect(self.screen, (0, 0, 0), (bar_x_enemy, bar_y_enemy, bar_width, bar_height), 2)

        health_ratio_enemy = self.enemy.hp / self.enemy.max_hp
        health_width_enemy = int(bar_width * health_ratio_enemy)
        pg.draw.rect(self.screen, (255, 0, 0), (bar_x_enemy, bar_y_enemy, health_width_enemy, bar_height))

        hp_text_enemy = font.render(f"{self.enemy.hp}/{self.enemy.max_hp}", True, (0, 0, 0))
        self.screen.blit(hp_text_enemy, (bar_x_enemy, bar_y_enemy - 25))

        if self.win == self.player:
            text = text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = text_render("...")
            text_rect2 = text2.get_rect(center=(...))
            self.screen.blit(text2, text_rect2)

        elif self.win == self.enemy:
            text = text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = text_render("...")
            text_rect2 = text2.get_rect(center=(...))
            self.screen.blit(text2, text_rect2)

        pg.display.flip()


if __name__ == "__main__":
    Menu()
