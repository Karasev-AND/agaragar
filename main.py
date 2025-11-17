import numpy as np
import pygame as pg
import numpy.random as random
import sys
from pygame.locals import *

pg.font.init()
pg.init()

window_height, window_width = 900, 1300
map_size = 1000
FPS = 30
game_over = False
bg_color = (210, 210, 210)
text_color = (0, 0, 0)
FONT = pg.font.SysFont("Comic Sans MS", 16)
clock = pg.time.Clock()
start_size = 25


food_amount = 100
bot_amount = 10


def get_rand_color():
    return random.randint(50, 180), random.randint(50, 180), random.randint(50, 180)


screen = pg.display.set_mode((window_width, window_height), pg.RESIZABLE)

pg.display.set_caption('agrario')
pg.time.Clock()


class Cell(object):
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius
        self.color = get_rand_color()
        self.speed = 3
        self.mass = radius * radius
        self.dx = 0
        self.dy = 0

    def draw(self, screen, camera_x, camera_y, screen_width, screen_height, zoom=1.0):
        screen_x = (self.x - camera_x) * zoom + screen_width // 2
        screen_y = (self.y - camera_y) * zoom + screen_height // 2
        scaled_radius = self.r * zoom

        if (-scaled_radius < screen_x < screen_width + scaled_radius and
                -scaled_radius < screen_y < screen_height + scaled_radius):
            pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(scaled_radius))

    def move(self, keys, cells):
        self.dx = 0
        self.dy = 0

        if keys[K_LEFT]:
            self.dx = -1
        if keys[K_RIGHT]:
            self.dx = 1
        if keys[K_UP]:
            self.dy = -1
        if keys[K_DOWN]:
            self.dy = 1

        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.7
            self.dy *= 0.7

        current_speed = self.speed * (200 / max(self.r, 200))

        new_x = self.x + self.dx * current_speed
        new_y = self.y + self.dy * current_speed

        can_move = True
        for cell in cells:
            if cell != self and cell.r > self.r * 0.8:
                distance_to_cell = np.sqrt((new_x - cell.x) ** 2 + (new_y - cell.y) ** 2)
                if distance_to_cell < self.r + cell.r - 5:
                    can_move = False
                    break

        if can_move:
            self.x = new_x
            self.y = new_y


class Food:
    def __init__(self):
        self.x = random.randint(-2000, 2000)
        self.y = random.randint(-2000, 2000)
        self.r = 5
        self.color = get_rand_color()

    def draw(self, screen, camera_x, camera_y, screen_width, screen_height, zoom=1.0):
        screen_x = (self.x - camera_x) * zoom + screen_width // 2
        screen_y = (self.y - camera_y) * zoom + screen_height // 2
        scaled_radius = self.r * zoom

        if (-scaled_radius < screen_x < screen_width + scaled_radius and
                -scaled_radius < screen_y < screen_height + scaled_radius):
            pg.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(scaled_radius))


class Bot(Cell):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.target_x = x
        self.target_y = y
        self.decision_timer = 0
        self.speed = 3

    def update(self, foods, cells, player):
        self.decision_timer -= 1

        if self.decision_timer <= 0:
            self.decision_timer = 30

            closest_food = None
            min_distance = float('inf')

            for food in foods:
                distance = np.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_food = food

            for cell in cells:
                if cell != self and cell.r < self.r * 0.8:
                    distance = np.sqrt((self.x - cell.x) ** 2 + (self.y - cell.y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_food = cell

            if closest_food:
                self.target_x = closest_food.x
                self.target_y = closest_food.y
            else:
                self.target_x = self.x + random.randint(-200, 200)
                self.target_y = self.y + random.randint(-200, 200)

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = max(np.sqrt(dx * dx + dy * dy), 0.1)
        dx /= distance
        dy /= distance

        current_speed = self.speed * (30 / max(self.r, 30))

        self.x += dx * current_speed
        self.y += dy * current_speed

        if player.r > self.r * 1.2:
            dx_to_player = self.x - player.x
            dy_to_player = self.y - player.y
            distance_to_player = np.sqrt(dx_to_player ** 2 + dy_to_player ** 2)

            if distance_to_player < 300:
                dx_to_player /= distance_to_player
                dy_to_player /= distance_to_player
                self.x += dx_to_player * current_speed * 1.5
                self.y += dy_to_player * current_speed * 1.5


import pygame
import random
import math
import sys

# Инициализация Pygame
pygame.init()

# Константы
INITIAL_WIDTH, INITIAL_HEIGHT = 1200, 800
FPS = 60
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Создание окна с возможностью изменения размера
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Agar.io Clone - Стрелки для управления")
clock = pygame.time.Clock()


def get_random_color():
    """Генерирует случайный яркий цвет"""
    return (
        random.randint(100, 255),
        random.randint(100, 255),
        random.randint(100, 255)
    )


class Cell:
    def __init__(self, x, y, radius, is_player=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = get_random_color() if not is_player else get_random_color()
        self.is_player = is_player
        self.speed = 5
        self.mass = radius * radius
        self.dx = 0
        self.dy = 0

    def draw(self, screen, camera_x, camera_y, screen_width, screen_height, zoom=1.0):
        # Рисуем клетку с учетом камеры, зума и текущего размера экрана
        screen_x = (self.x - camera_x) * zoom + screen_width // 2
        screen_y = (self.y - camera_y) * zoom + screen_height // 2
        scaled_radius = self.radius * zoom

        # Проверяем, находится ли клетка в пределах видимости
        if (-scaled_radius < screen_x < screen_width + scaled_radius and
                -scaled_radius < screen_y < screen_height + scaled_radius):
            # Рисуем основной круг
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(scaled_radius))

            # Для игрока добавляем контур
            if self.is_player:
                pygame.draw.circle(screen, GRAY, (int(screen_x), int(screen_y)), int(scaled_radius), 2)

    def move(self, keys, cells):
        if not self.is_player:
            return

        # Сбрасываем направление
        self.dx = 0
        self.dy = 0

        # Обрабатываем нажатия стрелок
        if keys[pygame.K_LEFT]:
            self.dx = -1
        if keys[pygame.K_RIGHT]:
            self.dx = 1
        if keys[pygame.K_UP]:
            self.dy = -1
        if keys[pygame.K_DOWN]:
            self.dy = 1

        # Нормализуем вектор движения (для диагонального движения)
        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.7071  # 1/√2
            self.dy *= 0.7071

        # Скорость зависит от размера (чем больше, тем медленнее)
        current_speed = self.speed * (30 / max(self.radius, 30))

        # Вычисляем новую позицию
        new_x = self.x + self.dx * current_speed
        new_y = self.y + self.dy * current_speed

        # Проверяем столкновения с другими клетками
        can_move = True
        for cell in cells:
            if cell != self and cell.radius > self.radius * 0.8:
                distance_to_cell = math.sqrt((new_x - cell.x) ** 2 + (new_y - cell.y) ** 2)
                if distance_to_cell < self.radius + cell.radius - 5:
                    can_move = False
                    break

        if can_move:
            self.x = new_x
            self.y = new_y


class Food:
    def __init__(self):
        self.x = random.randint(-2000, 2000)
        self.y = random.randint(-2000, 2000)
        self.radius = 5
        self.color = get_random_color()

    def draw(self, screen, camera_x, camera_y, screen_width, screen_height, zoom=1.0):
        screen_x = (self.x - camera_x) * zoom + screen_width // 2
        screen_y = (self.y - camera_y) * zoom + screen_height // 2
        scaled_radius = self.radius * zoom

        # Проверяем, находится ли еда в пределах видимости
        if (-scaled_radius < screen_x < screen_width + scaled_radius and
                -scaled_radius < screen_y < screen_height + scaled_radius):
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(scaled_radius))


class Bot(Cell):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.target_x = x
        self.target_y = y
        self.decision_timer = 0
        self.speed = 3

    def update(self, foods, cells, player):
        self.decision_timer -= 1

        # Принимаем решение каждые 30 кадров
        if self.decision_timer <= 0:
            self.decision_timer = 30

            # Ищем еду или маленькие клетки
            closest_food = None
            min_distance = float('inf')

            # Ищем ближайшую еду
            for food in foods:
                distance = math.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_food = food

            # Ищем маленькие клетки, которые можем съесть
            for cell in cells:
                if cell != self and cell.radius < self.radius * 0.8:
                    distance = math.sqrt((self.x - cell.x) ** 2 + (self.y - cell.y) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_food = cell

            # Если нашли цель, двигаемся к ней
            if closest_food:
                self.target_x = closest_food.x
                self.target_y = closest_food.y
            else:
                # Случайное движение
                self.target_x = self.x + random.randint(-200, 200)
                self.target_y = self.y + random.randint(-200, 200)

        # Двигаемся к цели
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = max(math.sqrt(dx * dx + dy * dy), 0.1)
        dx /= distance
        dy /= distance

        # Скорость зависит от размера
        current_speed = self.speed * (30 / max(self.radius, 30))

        self.x += dx * current_speed
        self.y += dy * current_speed

        # Избегаем игрока, если он больше
        if player.radius > self.radius * 1.2:
            dx_to_player = self.x - player.x
            dy_to_player = self.y - player.y
            distance_to_player = math.sqrt(dx_to_player ** 2 + dy_to_player ** 2)

            if distance_to_player < 300:  # Бежим, если игрок близко
                dx_to_player /= distance_to_player
                dy_to_player /= distance_to_player
                self.x += dx_to_player * current_speed * 1.5
                self.y += dy_to_player * current_speed * 1.5


class Game:
    def __init__(self):
        self.player = Cell(0, 0, 20, True)
        self.foods = [Food() for _ in range(500)]
        self.bots = [Bot(random.randint(-1500, 1500), random.randint(-1500, 1500),
                         random.randint(15, 30)) for _ in range(20)]
        self.cells = [self.player] + self.bots
        self.camera_x = 0
        self.camera_y = 0
        self.game_over = False
        self.win_mass = 5000  # Масса для победы
        self.zoom = 1.0
        self.min_zoom = 0.5  # Минимальный зум (максимальный обзор)
        self.max_zoom = 2.0  # Максимальный зум
        self.screen_width = INITIAL_WIDTH
        self.screen_height = INITIAL_HEIGHT

    def calculate_zoom(self):
        # Зум зависит от массы игрока - чем больше масса, тем больше обзор
        base_zoom = 1.0
        mass_factor = max(0, (self.player.mass - 400) / 5000)  # От 0 до 1
        zoom_level = base_zoom - (mass_factor * 0.5)  # Уменьшаем зум для большего обзора

        # Ограничиваем зум в допустимых пределах
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom_level))

    def handle_collisions(self):
        # Проверяем столкновения игрока с едой
        for food in self.foods[:]:
            distance = math.sqrt((self.player.x - food.x) ** 2 + (self.player.y - food.y) ** 2)
            if distance < self.player.radius:
                self.player.radius += 5
                self.player.mass = self.player.radius * self.player.radius
                self.foods.remove(food)
                self.foods.append(Food())

        # Проверяем столкновения игрока с ботами
        for bot in self.bots[:]:
            distance = math.sqrt((self.player.x - bot.x) ** 2 + (self.player.y - bot.y) ** 2)
            if distance < self.player.radius + bot.radius - 5:
                if self.player.radius > bot.radius * 1.1:
                    # Игрок съедает бота
                    self.player.radius += bot.radius * 0.3
                    self.player.mass = self.player.radius * self.player.radius
                    self.bots.remove(bot)
                    self.cells.remove(bot)
                    # Создаем нового бота
                    new_bot = Bot(random.randint(-1500, 1500), random.randint(-1500, 1500),
                                  random.randint(15, 30))
                    self.bots.append(new_bot)
                    self.cells.append(new_bot)
                elif bot.radius > self.player.radius * 1.1:
                    # Бот съедает игрока
                    self.game_over = True

        # Проверяем столкновения ботов с едой и друг с другом
        for bot in self.bots:
            # С едой
            for food in self.foods[:]:
                distance = math.sqrt((bot.x - food.x) ** 2 + (bot.y - food.y) ** 2)
                if distance < bot.radius:
                    bot.radius += 0.3
                    bot.mass = bot.radius * bot.radius
                    self.foods.remove(food)
                    self.foods.append(Food())

            # С другими ботами
            for other_bot in self.bots:
                if bot != other_bot:
                    distance = math.sqrt((bot.x - other_bot.x) ** 2 + (bot.y - other_bot.y) ** 2)
                    if distance < bot.radius + other_bot.radius - 5:
                        if bot.radius > other_bot.radius * 1.1:
                            bot.radius += other_bot.radius * 0.3
                            bot.mass = bot.radius * bot.radius
                            self.bots.remove(other_bot)
                            self.cells.remove(other_bot)
                            new_bot = Bot(random.randint(-1500, 1500), random.randint(-1500, 1500),
                                          random.randint(15, 30))
                            self.bots.append(new_bot)
                            self.cells.append(new_bot)
                            break

    def update_camera(self):
        self.camera_x = self.player.x
        self.camera_y = self.player.y

    def draw(self):
        # Получаем текущий размер окна
        current_width, current_height = screen.get_size()
        self.screen_width = current_width
        self.screen_height = current_height

        # Черный фон без сетки
        screen.fill(bg_color)

        # Рассчитываем зум
        self.calculate_zoom()

        # Рисуем еду
        for food in self.foods:
            food.draw(screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height, self.zoom)

        # Рисуем клетки
        for cell in self.cells:
            cell.draw(screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height, self.zoom)

        # Отображаем массу игрока
        font = pygame.font.SysFont(None, 36)
        mass_text = font.render(f"Масса: {int(self.player.mass)} / {self.win_mass}", True, (255, 255, 255))
        screen.blit(mass_text, (10, 10))

        # Инструкция по управлению
        controls_text = font.render("Управление: СТРЕЛКИ", True, (255, 255, 255))
        screen.blit(controls_text, (10, 50))

        # Информация о зуме
        zoom_text = font.render(f"Обзор: {self.zoom:.1f}x", True, (255, 255, 255))
        screen.blit(zoom_text, (10, 90))

        # Размер окна
        size_text = font.render(f"Окно: {self.screen_width}x{self.screen_height}", True, (200, 200, 200))
        screen.blit(size_text, (self.screen_width - 200, 10))

        # Проверяем победу
        if self.player.mass >= self.win_mass:
            win_text = font.render("ПОБЕДА! Вы достигли нужной массы!", True, (255, 255, 255))
            text_rect = win_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(win_text, text_rect)

        if self.game_over:
            game_over_text = font.render("ИГРА ОКОНЧЕНА! Вас съели!", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(game_over_text, text_rect)

    def run(self):
        running = True

        while running:
            # Получаем состояние всех клавиш
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Обрабатываем изменение размера окна
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if not self.game_over and self.player.mass < self.win_mass:
                # Обновляем позицию игрока (передаем нажатые клавиши)
                self.player.move(keys, self.cells)

                # Обновляем ботов
                for bot in self.bots:
                    bot.update(self.foods, self.cells, self.player)

                # Обрабатываем столкновения
                self.handle_collisions()

                # Обновляем камеру
                self.update_camera()

            # Рисуем всё
            self.draw()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
