import pygame
import sys
import random
from quad import QuadNode
from math import atan2, degrees, radians, sin, cos, pi
import numpy as np
from sliders import Slider


mode = "sandbox"
# mode = "evolution"

if mode == "evolution":
    screen_size = (640, 480)
    population = 100
    food_amt = 1000
    elit = 0.05
    screen = pygame.display.set_mode(screen_size)

    pygame.font.init()
    myfont = pygame.font.SysFont('Verdana', 15)
    textsurface = myfont.render('Epoch 0', False, (0, 0, 0))
    screen.blit(textsurface, (0, 0))

if mode == "sandbox":
    screen_size = (640, 480)
    population = 1
    food_amt = 1000
    screen = pygame.display.set_mode((screen_size[0], screen_size[1] + 70))
    slider1 = Slider("weight%d" % 1, 0, 1, -1, 10)
    slider2 = Slider("weight%d" % 2, 0, 1, -1, 120)
    slider3 = Slider("weight%d" % 3, 0, 1, -1, 230)
    slider4 = Slider("weight%d" % 4, 0, 1, -1, 340)
    slider5 = Slider("weight%d" % 5, 0, 1, -1, 450)
    sliders = [slider1, slider2, slider3, slider4, slider5]



# quad-tree for food tracking
food_qn = QuadNode(0, 0, screen_size[0], screen_size[1], 0)
food_qn.build(2)

# CELL IMAGE
CELL_IMG = pygame.Surface((6, 6), pygame.SRCALPHA)
pygame.draw.circle(CELL_IMG, (0, 255, 0), (3, 3), 3)
pygame.draw.rect(CELL_IMG, (0, 100, 0), (5, 2, 5, 3))
# (2, 0, 2, 1)

FOOD_IMG = pygame.Surface((2, 2), pygame.SRCALPHA)
pygame.draw.rect(FOOD_IMG, (100, 100, 10), (0, 0, 2, 2))


class Cell(pygame.sprite.Sprite):

    def __init__(self, origin, ih=None, ho=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = CELL_IMG
        self.rect = self.image.get_rect(center=origin)
        self.angle = random.randint(0, 359)
        self.score = 0
        if ih is None:
            self.ih = 2 * np.random.random_sample((1, 5)) - 1
        else:
            self.ih = ih
        if ho is None:
            self.ho = 2 * np.random.random_sample((5, 2)) - 1
        else:
            self.ho = ho

        self.af = lambda x: np.tanh(x)

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        self.image = pygame.transform.rotate(CELL_IMG, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        food_xy = self.n_food(food_qn)
        if food_xy is None:
            x = 0
            y = 0
            print('no food')
        else:
            x = food_xy[0]
            y = food_xy[1]

        f_angle = atan2(y - self.rect.y, x - self.rect.x)

        if self.angle > 180:
            tr_angle = self.angle - 360
        else:
            tr_angle = self.angle

        res_angle = f_angle - tr_angle / 180 * pi

        if res_angle > pi:
            res_angle -= 2 * pi
        elif res_angle < - pi:
            res_angle += 2 * pi

        norm_angle = res_angle / pi
        # print(self.ih)
        # print(self.ho)
        decision = self.af(np.dot(self.af(norm_angle * self.ih), self.ho))

        # print("des:", decision)
        # print("norm_angle:", norm_angle)
        rot = decision[0, 0]
        step = decision[0, 1]

        rot = rot * pi/4

        angle = rot + tr_angle / 180 * pi

        if step > 0:
            step = step * 4
        else:
            step = 0

        self.rect.y = (self.rect.y + step * sin(angle))  # % screen_size[1]
        if self.rect.y > screen_size[1]:
            self.rect.y = screen_size[1]
        if self.rect.y < 0:
            self.rect.y = 0

        self.rect.x = (self.rect.x + step * cos(angle))  # % screen_size[0]
        if self.rect.x > screen_size[0]:
            self.rect.x = screen_size[0]
        if self.rect.x < 0:
            self.rect.x = 0

        self.rotate(degrees(rot))
        collision_food = pygame.sprite.spritecollideany(self, foods)
        if collision_food is not None:
            collision_food.reset_pos(food_qn)
            self.score += 1

    def n_food(self, food_qn):
        min_dist = max(screen_size)
        nearest = None
        foods = food_qn.neighbours(self.rect.x, self.rect.y)

        for food in foods:
            dist = ((food.rect.x - self.rect.x) ** 2 + (food.rect.y - self.rect.y) ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist
                nearest = food
        if nearest is not None:
            # print(nearest.rect.x, nearest.rect.y, min_dist)
            return nearest.rect.x, nearest.rect.y
        else:
            return None


class Food(pygame.sprite.Sprite):
    def __init__(self, origin):
        pygame.sprite.Sprite.__init__(self)
        self.image = FOOD_IMG
        self.rect = self.image.get_rect(center=origin)

    def reset_pos(self, food_qn):
        obj = food_qn.pop(self.rect.x, self.rect.y)
        self.rect.x = random.randint(0, screen_size[0])
        self.rect.y = random.randint(0, screen_size[1])
        food_qn.add_xy_object(self.rect.x, self.rect.y, obj)

    def update(self):
        pass


def next_gen(cells):

    sort_cells = sorted([(cell, cell.score) for cell in cells], key=lambda x: x[1], reverse=True)
    top_ind = int(population*elit) - 1
    for i in range(top_ind, population):
        cell = sort_cells[i][0]
        a_cell = sort_cells[random.randint(0, top_ind)][0]
        b_cell = sort_cells[random.randint(0, top_ind)][0]

        # crossover
        rate = random.random()
        ih = rate * a_cell.ih + (1 - rate) * b_cell.ih
        ho = rate * a_cell.ho + (1 - rate) * b_cell.ho

        # mutation
        coin = random.randint(0, 1)

        if coin:
            ih[random.randint(0, ih.shape[0] - 1), random.randint(0, ih.shape[1] - 1)] *= random.uniform(0.5, 1.5)

        else:
            ho[random.randint(0, ho.shape[0] - 1), random.randint(0, ho.shape[1] - 1)] *= random.uniform(0.5, 1.5)

        cell.ih = ih
        cell.ho = ho
        cell.rect.x = random.randint(0, screen_size[0])
        cell.rect.y = random.randint(0, screen_size[1])




clock = pygame.time.Clock()

cells = pygame.sprite.Group()
for i in range(population):
    cells.add(Cell((random.randint(0, screen_size[0]), random.randint(0, screen_size[1]))))

# food init
foods = pygame.sprite.Group()
for i in range(food_amt):
    foods.add(Food((random.randint(0, screen_size[0]), random.randint(0, screen_size[1]))))

for food in foods:
    food_qn.add_xy_object(food.rect.x, food.rect.y, food)


time_to_evolve = 0
epoch = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for s in sliders:
                if s.button_rect.collidepoint(pos):
                    s.hit = True
        elif event.type == pygame.MOUSEBUTTONUP:
            for s in sliders:
                s.hit = False

    msElapsed = clock.tick(30)
    screen.fill((255, 255, 255))

    cells.draw(screen)
    foods.draw(screen)
    pygame.display.update()
    cells.update()

    if mode == "evolution":
        time_to_evolve += 1
        if time_to_evolve == 600:
            epoch += 1
            next_gen(cells)
            print("epoch:", epoch)
            time_to_evolve = 0
            textsurface = myfont.render('Epoch %d' % epoch, False, (0, 0, 0))

    if mode == "sandbox":

        for s in sliders:
            if s.hit:
                s.move()
        for s in sliders:
            s.draw()

        for cell in cells:
            for i in range(5):
                cell.ih[0, i] = sliders[i].val
    pygame.display.flip()
