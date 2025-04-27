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

# Synthetic binary data for sprites with animation frames
def generate_sprite_data(width, height, frames=1, seed=None):
    """Generate multiple frames of synthetic grayscale pixel data."""
    if seed is not None:
        random.seed(seed)  # Consistent sprites for same entity
    sprite_frames = []
    for _ in range(frames):
        data = bytearray()
        for _ in range(width * height):
            value = random.randint(0, 255) if random.random() > 0.3 else 0
            data.append(value)
        sprite_frames.append(data)
    return sprite_frames

def load_sprite_frames(data_list, width, height):
    """Convert list of frame data to list of Pygame surfaces."""
    surfaces = []
    for data in data_list:
        surface = pygame.Surface((width, height))
        for y in range(height):
            for x in range(width):
                idx = x + y * width
                value = data[idx]
                color = (value, value, value) if value > 0 else (0, 0, 0)
                surface.set_at((x, y), color)
        surfaces.append(surface)
    return surfaces

# Sprite data with animations
player_frames = generate_sprite_data(16, 16, frames=4, seed=1)  # 4-frame walk cycle
enemy_frames = generate_sprite_data(16, 16, frames=2, seed=2)   # 2-frame enemy wiggle
coin_frames = generate_sprite_data(8, 8, frames=4, seed=3)      # 4-frame coin spin
goal_data = generate_sprite_data(16, 32, frames=1, seed=4)[0]   # Static goal

player_sprites = load_sprite_frames(player_frames, 16, 16)
enemy_sprites = load_sprite_frames(enemy_frames, 16, 16)
coin_sprites = load_sprite_frames(coin_frames, 8, 8)
goal_sprite = load_sprite_frames([goal_data], 16, 32)[0]

# Platform data
platform_data = generate_sprite_data(32, 8, frames=1, seed=5)[0]
platform_sprite = load_sprite_frames([platform_data], 32, 8)[0]

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
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.1  # Frames per second per update

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

        # Animate if moving
        if self.vx != 0 or not self.on_ground:
            self.frame_timer += self.frame_speed
            if self.frame_timer >= 1:
                self.frame = (self.frame + 1) % len(player_sprites)
                self.frame_timer = 0
        else:
            self.frame = 0  # Idle frame

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

    def draw(self, screen):
        screen.blit(player_sprites[self.frame], (self.rect.x, self.rect.y))

class Platform:
    def __init__(self, x, y, width=32, height=8):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        screen.blit(platform_sprite, (self.rect.x, self.rect.y))

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vx = -1
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.05

    def update(self):
        self.rect.x += self.vx
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vx = -self.vx
        # Animate
        self.frame_timer += self.frame_speed
        if self.frame_timer >= 1:
            self.frame = (self.frame + 1) % len(enemy_sprites)
            self.frame_timer = 0

    def draw(self, screen):
        screen.blit(enemy_sprites[self.frame], (self.rect.x, self.rect.y))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.15

    def update(self):
        # Animate
        self.frame_timer += self.frame_speed
        if self.frame_timer >= 1:
            self.frame = (self.frame + 1) % len(coin_sprites)
            self.frame_timer = 0

    def draw(self, screen):
        screen.blit(coin_sprites[self.frame], (self.rect.x, self.rect.y))

class Goal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 32)

    def draw(self, screen):
        screen.blit(goal_sprite, (self.rect.x, self.rect.y))

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
    for coin in coins:
        coin.update()
    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            player.score += 10
            coins.remove(coin)
    if player.rect.colliderect(goal.rect):
        print(f"Level Complete! Score: {player.score}")
        running = False

    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            player.vx, player.vy = 0, 0
            player.score = max(0, player.score - 10)

    # Draw
    screen.fill((92, 148, 252))  # SMW sky blue
    for p in platforms:
        p.draw(screen)
    for e in enemies:
        e.draw(screen)
    for c in coins:
        c.draw(screen)
    goal.draw(screen)
    player.draw(screen)

    # Score display
    font = pygame.font.Font(None, 24)
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
