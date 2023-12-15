import pygame
import os
import random
from pygame.math import Vector2 as vec

pygame.init()
running = True
WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS")

FPS = 60
clock = pygame.time.Clock()

DAS = 6 # Delayed Auto Shift : 꾹 눌렀다고 인식하기까지 걸리는 시간 (단위 : 프레임)
ARR = 1 # Auto Repeat Rate : 꾹 눌렀을 떄 한 칸씩 움직이는 데 걸리는 시간 (단위 : 프레임)
GRAV = 0.05 # 미노가 내려오는 속도 (기본 : 20프레임에 한 칸)


CONTROLS = {
    "LEFT" : pygame.K_k, # 왼쪽으로 이동
    "RIGHT" : pygame.K_SEMICOLON, # 오른쪽으로 이동
    "CW" : pygame.K_o, # 시계방향으로 회전
    "CCW" : pygame.K_a, # 반시계방향으로 회전
    "180" : pygame.K_s, # 180도 회전
    "HD" : pygame.K_SPACE, # 한번에 내려가기
    "SD" : pygame.K_l, # 빠르게 내려가기
    "HOLD" : pygame.K_LSHIFT # 현재 미노 저장
}

font = pygame.font.SysFont("arial", 30, True, True) # 게임 폰트
##############색깔 지정####################
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
############################################

PIXEL = pygame.Surface((20, 20)) # 미노를 구성할 픽셀 크기
HOLD_GRID = pygame.Surface((100, 100)) # 저장해둔 미노 표시할 곳
NEXT_GRID = pygame.Surface((100, 500)) # 다음으로 나올 미노 표시할 곳
pygame.draw.rect(HOLD_GRID, GRAY, [0, 0, 100, 100], 1)
pygame.draw.rect(NEXT_GRID, GRAY, [0, 0, 100, 500], 1)

BOARD = [[[0, 0] for i in range(10)] for j in range(21)] #미노가 떨어질 보드 BOARD[y][x][0]은 미노의 상태, BOARD[y][x][1]은 미노의 종류
#상태가 0 : 없음, 1 : 떨어지는 중, 2 : 이미 떨어짐
NEXT = ["I", "O", "T", "L", "J", "S", "Z"] # 다음으로 나올 미노들
AFTER_NEXT = [i for i in NEXT] # 그 다음으로 나올 미노들
random.shuffle(NEXT) 
random.shuffle(AFTER_NEXT) # 랜덤으로 섞기
TOTAL_NEXT = NEXT + AFTER_NEXT
cnt = 0 # 현재 미노가 현재 가방에서 몇 번째 미노인지 (0 ~ 6)
CURRENT_NEXT = [i for i in TOTAL_NEXT]

TETROMINOS = {
    "I" : [vec(-1, 0), vec(-2, 0), vec(0, 0), vec(1, 0)],
    "O" : [vec(-1, -1), vec(-1, 0), vec(0, 0), vec(0, -1)],
    "T" : [vec(-1, 0), vec(0, 0), vec(1, 0), vec(0, -1)],
    "L" : [vec(1, -1), vec(1, 0), vec(0, 0), vec(-1, 0)],
    "J" : [vec(-1, -1), vec(-1, 0), vec(0, 0), vec(1, 0)],
    "S" : [vec(-1, 0), vec(0, 0), vec(0, -1), vec(1, -1)],
    "Z" : [vec(1, 0), vec(0, 0), vec(0, -1), vec(-1, -1)]
} # 미노마다 모양 정의 vec(-1, -1)은 vec(0, 0)에서 왼쪽으로 한칸, 위로 한칸

COLORS = {
    "I" : SKY,
    "O" : YELLOW,
    "T" : MAGENTA,
    "L" : ORANGE,
    "J" : BLUE,
    "S" : GREEN,
    "Z" : RED
} # 미노마다 색깔 정의


grid_thick = 1 # 그리드 두께
grid_gap = 20 # 그리드 간격

x_grid = pygame.Surface((grid_gap * 10, grid_thick)) # 수평 그리드
y_grid = pygame.Surface((grid_thick, grid_gap * 20)) # 수직 그리드
x_grid.fill(GRAY)
y_grid.fill(GRAY)

class Block: # 미노 클래스
    def __init__(self, block): # 초기 조건
        self.pos = vec(4, 1) # 보드에서 미노의 중심의 위치
        self.block = block # 미노 종류
        self.realposy = 1 # realposy를 정수로 바꿔서 pos.y에 넣음
        self.pixels = TETROMINOS[self.block] # 미노 모양
    
    def fall(self): # 미노를 떨어뜨림
        self.realposy += GRAV 
        self.pos.y = int(self.realposy)

    def fallen(self): # 미노가 바닥에 닿았을 때
        for j in self.pixels:
            BOARD[int(self.pos.y + j.y)][int(self.pos.x + j.x)] = [2, self.block]

    def iscollide(self): # 미노가 바닥에 닿았는지
        for i in self.pixels:
            place_to_fall = self.pos + i + vec(0, 1)
            if int(place_to_fall.y) == 21:
                return True
            elif BOARD[int(place_to_fall.y)][int(place_to_fall.x)][0] == 2:
                return True
        return False
    
    def update(self): # 자신의 위치를 보드에 입력
        for i in self.pixels:
            BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)] = [1, self.block]

    def canleft(self): # 왼쪽으로 갈 수 있는 지
        for i in self.pixels:
            if self.pos.x + i.x < 1:
                return False
        for i in self.pixels:
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x - 1)][0] == 2:
                return False
        return True
                
    def canright(self): # 오른쪽으로 갈 수 있는 지
        for i in self.pixels:
            if self.pos.x + i.x > 8:
                return False
        for i in self.pixels:
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x + 1)][0] == 2:
                return False
        return True
    
    def canclockwise(self): # 시계방향으로 돌 수 있는 지
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
    
    def cancounterclockwise(self): # 반시계방향으로 돌 수 있는 지
        to_rotate = [vec(i.y, -i.x) for i in self.pixels]
        for i in to_rotate:
            if self.pos.x + i.x < 1:
                return False
            if self.pos.x + i.x > 9:
                return False
            if BOARD[int(self.pos.y + i.y)][int(self.pos.x + i.x)][0] == 2:
                return False
        return True
    
    def can180(self): # 180도 회전을 할 수 있는 지
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
        
        
    
    def shadow(self): # 미노가 떨어질 위치 표시
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
                    
            
            

PIECE = Block(NEXT[cnt]) # 현재 떨어지는 미노
cnt += 1 # 

HOLD = 0 # 저장되있는 미노
HOLD_USED = 0 # 저장은 미노당 한 번만 가능
score = 0 # 점수



#########################################################

while running:
    clock.tick(FPS)

    print(cnt)
    TOTAL_NEXT = NEXT + AFTER_NEXT # 다음 미노들 (14개)
    

    for line in BOARD: # 떨어지는 중인 미노 흔적 없애기
        for j in line:
            if j[0] == 1:
                j[0] = 0
                j[1] = 0


    PIECE.update()
    place = False # 미노가 떨어져서 그 위치에 고정되어야 하는 지


    if PIECE.iscollide():
        place = True

    if place:
        placetime += 1 
        if placetime >= 30: # 30프레임이 지나면 그대로 설치 (회전, 이동을 하면 초기화)
            PIECE.fallen()
            PIECE = Block(NEXT[cnt]) # 다음 미노로 바꾸기
            cnt += 1
            CURRENT_NEXT.remove(CURRENT_NEXT[0])
            HOLD_USED = 0
    else:
        PIECE.fall() # 아니면 그냥 계속 떨어짐
        placetime = 0

    if cnt == 7: # 가방안에 있는 미노 다 쓰면 초기화
        cnt = 0
        NEXT = [i for i in AFTER_NEXT]
        random.shuffle(AFTER_NEXT)
        CURRENT_NEXT += AFTER_NEXT

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN: # 키를 눌렀나
            if event.key == CONTROLS["HD"]: # 한 번에 내려가기
                PIECE.realposy = int(PIECE.realposy)
                PIECE.realposy += PIECE.shadow()[1]
                PIECE.pos.y = int(PIECE.realposy)
                PIECE.fallen()
                PIECE = Block(NEXT[cnt])
                cnt += 1
                CURRENT_NEXT.remove(CURRENT_NEXT[0])
                HOLD_USED = 0
                    

            if event.key == CONTROLS["CW"]: # 시계방향
                if PIECE.canclockwise():
                    PIECE.pixels = [vec(-i.y, i.x) for i in PIECE.pixels]
                    placetime = 0

            if event.key == CONTROLS["CCW"]: # 반시계방향
                if PIECE.cancounterclockwise():
                    PIECE.pixels = [vec(i.y, -i.x) for i in PIECE.pixels]
                    placetime = 0

            if event.key == CONTROLS["180"]: # 180도
                if PIECE.can180():
                    PIECE.pixels = [vec(-i.x, -i.y) for i in PIECE.pixels]
                    placetime = 0
            
            if event.key == CONTROLS["HOLD"] and HOLD_USED == 0: # 저장
                if HOLD == 0:
                    HOLD = PIECE.block
                    PIECE = Block(NEXT[cnt])
                    cnt += 1
                    CURRENT_NEXT.remove(CURRENT_NEXT[0])
                    HOLD_USED = 1
                else:    
                    TEMP = HOLD
                    HOLD = PIECE.block
                    PIECE = Block(TEMP)
                    HOLD_USED = 1
                

    keys = pygame.key.get_pressed()
    if keys[CONTROLS["SD"]]: # 빨리 내려가기
        GRAV = 1 # 중력 세게
    else:
        GRAV = 0.05

    if keys[CONTROLS["RIGHT"]]: # 오른쪽
        if PIECE.canright() and (righttime == 0 or (righttime >= DAS and righttime % ARR == 0)): # 꾹 눌렀나
            PIECE.pos.x += 1
            placetime = 0
        righttime += 1
    else:
        righttime = 0
    
    if keys[CONTROLS["LEFT"]]: # 왼쪽
        if PIECE.canleft() and (lefttime == 0 or (lefttime >= DAS and lefttime % ARR == 0)):
            PIECE.pos.x -= 1
            placetime = 0
        lefttime += 1
    else:
        lefttime = 0
        


    row = 0
    for line in BOARD:
        isfill = 1
        for j in line: # 그 줄이 다 찼는지
            if j[0] != 2:
                isfill = 0
        if isfill:
            score += 1 #한 줄당 1점
            BOARD[row] = [[0, 0] for i in range(10)] # 줄 지우기
            for i in range(row):
                BOARD[row - i] = [[k[0], k[1]] for k in BOARD[row - i - 1]] # 지워진 줄 위에 있는 줄들 아래로 내리기
        row += 1
            

    screen.fill(BLACK) # 배경색

    for i in PIECE.shadow()[0]: # 미노 떨어질 위치 표시
        PIXEL.fill(GRAY) 
        screen.blit(PIXEL, (i[0] * 20 + 200, i[1] * 20 + 80))


    for i in range(21):
        screen.blit(x_grid, (200, 100 + grid_gap * i - grid_thick / 2))
    for i in range(11):
        screen.blit(y_grid, (200 + grid_gap * i - grid_thick / 2, 100))
    row = 0
    for line in BOARD: # 보드 내용 스크린에 표시
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
    if HOLD != 0: #저장 미노 스크린에 표시
        for i in TETROMINOS[HOLD]:
            PIXEL.fill(COLORS[HOLD])
            HOLD_GRID.blit(PIXEL, (40 + i.x * 20, 40 + i.y * 20))
    
    screen.blit(NEXT_GRID, (450, 50))
    NEXT_GRID.fill(BLACK)
    pygame.draw.rect(NEXT_GRID, GRAY, [0, 0, 100, 500], 1)
    NEXT_IDX = 0
    for i in CURRENT_NEXT[1:6]: # 다음 미노들 스크린에 표시
        for j in TETROMINOS[i]:
            PIXEL.fill(COLORS[i])
            NEXT_GRID.blit(PIXEL, (40 + j.x * 20, 40 + j.y * 20 + NEXT_IDX * 100))
        NEXT_IDX += 1
    
    



    pygame.display.update() # 화면 업데이트

pygame.quit()
