import pygame
import sys
import random

# Pygame Setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 256, 240
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ZeroCoin SMB1")
clock = pygame.time.Clock()
FPS = 60

# Colors
COLOR_BG = (92, 148, 252)
COLOR_BRICK = (200, 76, 12)
COLOR_COIN = (255, 223, 0)
COLOR_PLAYER = (255, 0, 0)
COLOR_GROUND = (106, 190, 48)
COLOR_FLAG = (255, 255, 255)

# Player Class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vx, self.vy = 0, 0
        self.speed = 2
        self.jump_power = -8
        self.gravity = 0.4
        self.on_ground = False
        self.score = 0

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed
        if keys[pygame.K_z] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self.vy += self.gravity
        self.rect.x += self.vx
        self.collide(self.vx, 0, platforms)
        self.rect.y += self.vy
        self.on_ground = False
        self.collide(0, self.vy, platforms)

        if self.rect.y > SCREEN_HEIGHT:
            self.respawn()

    def respawn(self):
        self.rect.x, self.rect.y = 32, 180
        self.vx, self.vy = 0, 0

    def collide(self, dx, dy, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if dx > 0:
                    self.rect.right = p.rect.left
                if dx < 0:
                    self.rect.left = p.rect.right
                if dy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

# Platform Class
class Platform:
    def __init__(self, x, y, w=16, h=16, color=COLOR_BRICK):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

# Coin Class
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 8, 8)

# Flag Class
class Flag:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 8, 32)

# World Generation (Synthetic from imagination)
platforms = []
coins = []

# Ground
for x in range(0, 3000, 16):
    platforms.append(Platform(x, SCREEN_HEIGHT - 16, 16, 16, COLOR_GROUND))

# Bricks
for i in range(5):
    platforms.append(Platform(100 + i*18, 150, 16, 16))

for i in range(3):
    platforms.append(Platform(250 + i*18, 120, 16, 16))

# Random Coins
for i in range(10):
    coins.append(Coin(random.randint(100, 800), random.randint(80, 180)))

# Flag
flag = Flag(900, SCREEN_HEIGHT - 48)

# Entities
player = Player(32, 180)

# Camera Offset
scroll_x = 0

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    player.update(platforms)

    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            player.score += 100
            coins.remove(coin)

    if player.rect.colliderect(flag.rect):
        print(f"LEVEL COMPLETE! SCORE: {player.score}")
        running = False

    # Scroll Camera
    scroll_x = player.rect.x - 64

    # Draw
    screen.fill(COLOR_BG)

    for p in platforms:
        pygame.draw.rect(screen, p.color, pygame.Rect(p.rect.x - scroll_x, p.rect.y, p.rect.width, p.rect.height))

    for c in coins:
        pygame.draw.rect(screen, COLOR_COIN, pygame.Rect(c.rect.x - scroll_x, c.rect.y, c.rect.width, c.rect.height))

    pygame.draw.rect(screen, COLOR_FLAG, pygame.Rect(flag.rect.x - scroll_x, flag.rect.y, flag.rect.width, flag.rect.height))
    pygame.draw.rect(screen, COLOR_PLAYER, pygame.Rect(player.rect.x - scroll_x, player.rect.y, player.rect.width, player.rect.height))

    # Score Display
    font = pygame.font.SysFont(None, 24)
    score_surf = font.render(f"Score: {player.score}", True, (255,255,255))
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
