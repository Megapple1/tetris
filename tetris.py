import pygame
import os
import random
from pygame.math import Vector2 as vec

pygame.init()
running = True

CURRENT_FILE = os.getcwd()
IMAGE_FILE = os.path.join(CURRENT_FILE, "images")

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS")

FPS = 60
clock = pygame.time.Clock()

DAS = 7
ARR = 1
CONTROLS = {
    "LEFT" : pygame.K_k,
    "RIGHT" : pygame.K_SEMICOLON,
    "CW" : pygame.K_o,
    "CCW" : pygame.K_a,
    "180" : pygame.K_s,
    "HD" : pygame.K_SPACE,
    "SD" : pygame.K_l,
    "HOLD" : pygame.K_LSHIFT
}

font = pygame.font.SysFont("arial", 30, True, True)


WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
ORANGE = (255, 100, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
SKY = (0, 127, 255)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

PIXEL = pygame.Surface((20, 20))
HOLD_GRID = pygame.Surface((100, 100))
NEXT_GRID = pygame.Surface((100, 500))
pygame.draw.rect(HOLD_GRID, GRAY, [0, 0, 100, 100], 1)
pygame.draw.rect(NEXT_GRID, GRAY, [0, 0, 100, 500], 1)

BOARD = [[[0, 0] for i in range(10)] for j in range(21)] #BOARD[y][x][0] = 0 -> none, 1 -> falling 2 -> fallen, BOARD[y][x][1] = block etc) [1, "O"]
GRAV = 0.05
NEXT = ["I", "O", "T", "L", "J", "S", "Z"]
AFTER_NEXT = [i for i in NEXT]
random.shuffle(NEXT)
random.shuffle(AFTER_NEXT)
cnt = 0


TETROMINOS = {
    "I" : [vec(-1, 0), vec(-2, 0), vec(0, 0), vec(1, 0)],
    "O" : [vec(-1, -1), vec(-1, 0), vec(0, 0), vec(0, -1)],
    "T" : [vec(-1, 0), vec(0, 0), vec(1, 0), vec(0, -1)],
    "L" : [vec(1, -1), vec(1, 0), vec(0, 0), vec(-1, 0)],
    "J" : [vec(-1, -1), vec(-1, 0), vec(0, 0), vec(1, 0)],
    "S" : [vec(-1, 0), vec(0, 0), vec(0, -1), vec(1, -1)],
    "Z" : [vec(1, 0), vec(0, 0), vec(0, -1), vec(-1, -1)]
}

COLORS = {
    "I" : SKY,
    "O" : YELLOW,
    "T" : MAGENTA,
    "L" : ORANGE,
    "J" : BLUE,
    "S" : GREEN,
    "Z" : RED
}


grid_thick = 1
grid_gap = 20

x_grid = pygame.Surface((grid_gap * 10, grid_thick))
y_grid = pygame.Surface((grid_thick, grid_gap * 20))
x_grid.fill(GRAY)
y_grid.fill(GRAY)

class Block:
    def __init__(self, block):
        self.pos = vec(4, 1)
        self.block = block
        self.realposy = 1
        self.pixels = TETROMINOS[self.block]
    
    def fall(self):
        self.realposy += GRAV
        self.pos.y = int(self.realposy)

    def fallen(self):
        for j in self.pixels:
            BOARD[int(self.pos.y + j.y)][int(self.pos.x + j.x)] = [2, self.block]

    def iscollide(self):
        for i in self.pixels:
            place_to_fall = self.pos + i + vec(0, 1)
            if int(place_to_fall.y) == 21:
                return True
            elif BOARD[int(place_to_fall.y)][int(place_to_fall.x)][0] == 2:
                return True
        return False
    
    def update(self):
        for i in self.pixels:
            BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)] = [1, self.block]

    def canleft(self):
        for i in self.pixels:
            if self.pos.x + i.x < 1:
                return False
        for i in self.pixels:
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x - 1)][0] == 2:
                return False
        return True
                
    def canright(self):
        for i in self.pixels:
            if self.pos.x + i.x > 8:
                return False
        for i in self.pixels:
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x + 1)][0] == 2:
                return False
        return True
    
    def canclockwise(self):
        to_rotate = [vec(-i.y, i.x) for i in self.pixels]
        for i in to_rotate:
            if self.pos.x + i.x < 1:
                return False
            if self.pos.x + i.x > 9:
                return False
                self.canclockwise()
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)][0] == 2:
                return False
        return True
    
    def cancounterclockwise(self):
        to_rotate = [vec(i.y, -i.x) for i in self.pixels]
        for i in to_rotate:
            if self.pos.x + i.x < 1:
                return False
            if self.pos.x + i.x > 9:
                return False
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)][0] == 2:
                return False
        return True
    
    def can180(self):
        to_rotate = [vec(-i.x, -i.y) for i in self.pixels]
        for i in to_rotate:
            # if self.pos.x + i.x < 1:
            #     self.pos.x += 1
            #     self.cancounterclockwise()
            # if self.pos.x + i.x > 9:
            #     self.pos.x -= 1
            #     self.cancounterclockwise()
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)][0] == 2:
                return False
        return True
        
        
    
    def shadow(self):
        distances = []
        for i in self.pixels:
            j = 0
            while True:
                j += 1
                if int(self.pos.y + i.y + j) == 21:
                    j -= 1
                    break
                elif BOARD[int(self.pos.y + i.y + j)][int(self.pos.x + i.x)][0] == 2:
                    j -= 1
                    break
            distances.append(j)
        shadows = [[int(self.pos.x + i.x), int(self.pos.y + i.y + min(distances))] for i in self.pixels]
        return [shadows, min(distances)]
                    
            
            

PIECE = Block(NEXT[cnt])
cnt += 1

HOLD = 0
HOLD_USED = 0
score = 0



#########################################################

while running:
    clock.tick(FPS)

    print(score)
    TOTAL_NEXT = NEXT + AFTER_NEXT

    for line in BOARD:
        for j in line:
            if j[0] == 1:
                j[0] = 0
                j[1] = 0


    PIECE.update()
    place = False


    if PIECE.iscollide():
        place = True

    if place:
        placetime += 1
        if placetime >= 30:
            PIECE.fallen()
            PIECE = Block(NEXT[cnt])
            cnt += 1
            HOLD_USED = 0
    else:
        PIECE.fall()
        placetime = 0

    if cnt == 7:
        cnt = 0
        NEXT = [i for i in AFTER_NEXT]
        random.shuffle(AFTER_NEXT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == CONTROLS["HD"]:
                PIECE.realposy = int(PIECE.realposy)
                PIECE.realposy += PIECE.shadow()[1]
                PIECE.pos.y = int(PIECE.realposy)
                PIECE.fallen()
                PIECE = Block(NEXT[cnt])
                cnt += 1
                HOLD_USED = 0
                    

            if event.key == CONTROLS["CW"]:
                if PIECE.canclockwise():
                    PIECE.pixels = [vec(-i.y, i.x) for i in PIECE.pixels]
                    placetime = 0

            if event.key == CONTROLS["CCW"]:
                if PIECE.cancounterclockwise():
                    PIECE.pixels = [vec(i.y, -i.x) for i in PIECE.pixels]
                    placetime = 0

            if event.key == CONTROLS["180"]:
                if PIECE.can180():
                    PIECE.pixels = [vec(-i.x, -i.y) for i in PIECE.pixels]
                    placetime = 0
            
            if event.key == CONTROLS["HOLD"] and HOLD_USED == 0:
                if HOLD == 0:
                    HOLD = PIECE.block
                    PIECE = Block(NEXT[cnt])
                    cnt += 1
                    HOLD_USED = 1
                else:    
                    TEMP = HOLD
                    HOLD = PIECE.block
                    PIECE = Block(TEMP)
                    cnt += 1
                    HOLD_USED = 1
                

    keys = pygame.key.get_pressed()
    if keys[CONTROLS["SD"]]:
        GRAV = 1
    else:
        GRAV = 0.05

    if keys[CONTROLS["RIGHT"]]:
        if PIECE.canright() and (righttime == 0 or (righttime >= DAS and righttime % ARR == 0)):
            PIECE.pos.x += 1
            placetime = 0
        righttime += 1
    else:
        righttime = 0
    
    if keys[CONTROLS["LEFT"]]:
        if PIECE.canleft() and (lefttime == 0 or (lefttime >= DAS and lefttime % ARR == 0)):
            PIECE.pos.x -= 1
            placetime = 0
        lefttime += 1
    else:
        lefttime = 0
        


    row = 0
    for line in BOARD:
        isfill = 1
        for j in line:
            if j[0] != 2:
                isfill = 0
        if isfill:
            score += 1
            BOARD[row] = [[0, 0] for i in range(10)]
            for i in range(row):
                BOARD[row - i] = [[k[0], k[1]] for k in BOARD[row - i - 1]]
        row += 1
            

    screen.fill(BLACK)

    for i in PIECE.shadow()[0]:
        PIXEL.fill(GRAY)
        screen.blit(PIXEL, (i[0] * 20 + 200, i[1] * 20 + 80))


    for i in range(21):
        screen.blit(x_grid, (200, 100 + grid_gap * i - grid_thick / 2))
    for i in range(11):
        screen.blit(y_grid, (200 + grid_gap * i - grid_thick / 2, 100))
    row = 0
    for line in BOARD:
        column = 0
        for j in line:
            if j[0] != 0:
                PIXEL.fill(COLORS[j[1]])
                screen.blit(PIXEL, (column * 20 + 200, row * 20 + 80))
            column += 1
        row += 1
    screen.blit(HOLD_GRID, (50, 100))
    HOLD_GRID.fill(BLACK)
    pygame.draw.rect(HOLD_GRID, GRAY, [0, 0, 100, 100], 1)
    if HOLD != 0:
        for i in TETROMINOS[HOLD]:
            PIXEL.fill(COLORS[HOLD])
            HOLD_GRID.blit(PIXEL, (40 + i.x * 20, 40 + i.y * 20))
    
    screen.blit(NEXT_GRID, (450, 50))
    NEXT_GRID.fill(BLACK)
    pygame.draw.rect(NEXT_GRID, GRAY, [0, 0, 100, 500], 1)
    NEXT_IDX = 0
    for i in TOTAL_NEXT[(cnt):((cnt+5))]:
        for j in TETROMINOS[i]:
            PIXEL.fill(COLORS[i])
            NEXT_GRID.blit(PIXEL, (40 + j.x * 20, 40 + j.y * 20 + NEXT_IDX * 100))
        NEXT_IDX += 1
    
    



    pygame.display.update()

pygame.quit()