# test.py
import pygame
import sys
import struct
import random

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 256, 224
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario World Clone (RAW)")
clock = pygame.time.Clock()
FPS = 60

# Synthetic binary data for sprites (mocked, no PNGs)
def generate_sprite_data(width, height):
    # Generate synthetic grayscale pixel data
    data = bytearray()
    for _ in range(width * height):
        value = random.randint(0, 255) if random.random() > 0.3 else 0
        data.append(value)
    return data

def load_sprite(data, width, height):
    surface = pygame.Surface((width, height))
    for y in range(height):
        for x in range(width):
            idx = x + y * width
            value = data[idx]
            color = (value, value, value) if value > 0 else (0, 0, 0)
            surface.set_at((x, y), color)
    return surface

# Sprite data
player_data = generate_sprite_data(16, 16)
enemy_data = generate_sprite_data(16, 16)
coin_data = generate_sprite_data(8, 8)
goal_data = generate_sprite_data(16, 32)

player_sprite = load_sprite(player_data, 16, 16)
enemy_sprite = load_sprite(enemy_data, 16, 16)
coin_sprite = load_sprite(coin_data, 8, 8)
goal_sprite = load_sprite(goal_data, 16, 32)

# Platform data (synthetic, hardcoded)
platform_data = generate_sprite_data(32, 8)
platform_sprite = load_sprite(platform_data, 32, 8)

# Game entities
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
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self.vy += self.gravity
        self.rect.x += self.vx
        self.collide(self.vx, 0, platforms)
        self.rect.y += self.vy
        self.on_ground = False
        self.collide(0, self.vy, platforms)

        if self.rect.y > SCREEN_HEIGHT:
            self.rect.x, self.rect.y = 16, 16
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

class Platform:
    def __init__(self, x, y, width=32, height=8):
        self.rect = pygame.Rect(x, y, width, height)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vx = -1

    def update(self):
        self.rect.x += self.vx
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vx = -self.vx

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 8, 8)

class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 32)

# Level setup
player = Player(16, 16)
platforms = [
    Platform(0, 200, 256, 8),  # Ground
    Platform(80, 160, 64, 8),
    Platform(150, 120, 64, 8),
]
enemies = [Enemy(100, 184), Enemy(180, 104)]
coins = [Coin(90, 140), Coin(160, 100), Coin(200, 100)]
goal = Goal(220, 168)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    player.update(platforms)
    for enemy in enemies:
        enemy.update()
    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            player.score += 10
            coins.remove(coin)
    if player.rect.colliderect(goal.rect):
        print(f"Level Complete! Score: {player.score}")
        running = False

    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            player.rect.x, player.rect.y = 16, 16
            player.vx, player.vy = 0, 0
            player.score = max(0, player.score - 10)

    # Draw
    screen.fill((92, 148, 252))  # SMW sky blue
    for p in platforms:
        screen.blit(platform_sprite, (p.rect.x, p.rect.y))
    for e in enemies:
        screen.blit(enemy_sprite, (e.rect.x, e.rect.y))
    for c in coins:
        screen.blit(coin_sprite, (c.rect.x, c.rect.y))
    screen.blit(goal_sprite, (goal.rect.x, goal.rect.y))
    screen.blit(player_sprite, (player.rect.x, player.rect.y))

    # Score display
    font = pygame.font.Font(None, 24)
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
