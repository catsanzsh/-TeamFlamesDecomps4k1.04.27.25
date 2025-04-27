import pygame
import sys

# Pygame Setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 256, 240  # NES resolution
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros. 1 Clone")
clock = pygame.time.Clock()
FPS = 60

# Colors (approximating SMB1 palette)
COLOR_BG = (92, 148, 252)       # Sky blue
COLOR_GROUND = (139, 69, 19)    # Brown dirt
COLOR_BRICK = (200, 76, 12)     # Brick orange
COLOR_QBLOCK = (255, 215, 0)    # Question block yellow
COLOR_COIN = (255, 223, 0)      # Coin gold
COLOR_PLAYER = (255, 0, 0)      # Mario red
COLOR_GOOMBA = (139, 69, 19)    # Goomba brown
COLOR_PIPE = (0, 128, 0)        # Pipe green
COLOR_FLAGPOLE = (169, 169, 169) # Flagpole gray
COLOR_FLAG = (255, 255, 255)    # Flag white

# Tile Size
TILE_SIZE = 16

# Player Class
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
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
        if keys[pygame.K_SPACE] and self.on_ground:  # Space to jump
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
        self.rect.x, self.rect.y = TILE_SIZE * 2, SCREEN_HEIGHT - TILE_SIZE * 3
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
    def __init__(self, x, y, w=TILE_SIZE, h=TILE_SIZE, color=COLOR_BRICK):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

# Coin Class
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 4, y + 4, 8, 8)  # Smaller for coin

# Enemy Class (Goomba)
class Goomba:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = -1  # Moves left
    def update(self):
        self.rect.x += self.vx
        if self.rect.x < 0 or self.rect.x > 3000:  # Reverse direction at bounds
            self.vx = -self.vx

# Pipe Class
class Pipe:
    def __init__(self, x, y, height):
        self.rect = pygame.Rect(x, y - (height - 1) * TILE_SIZE, TILE_SIZE * 2, height * TILE_SIZE)
    def draw(self, screen, scroll_x):
        pygame.draw.rect(screen, COLOR_PIPE, (self.rect.x - scroll_x, self.rect.y, self.rect.width, self.rect.height))

# Flag Class
class Flag:
    def __init__(self, x, y):
        self.pole = pygame.Rect(x, y - TILE_SIZE * 8, 4, TILE_SIZE * 8)  # Flagpole
        self.flag = pygame.Rect(x - 8, y - TILE_SIZE * 8, TILE_SIZE, TILE_SIZE)  # Flag

# Level Data for World 1-1 (simplified representation)
# '#' = ground, 'B' = brick, '?' = question block, 'C' = coin, 'G' = Goomba, 'P' = pipe, 'F' = flag
level_1_1 = [
    "........................................................................................",
    "........................................................................................",
    "........................................................................................",
    "........................................................................................",
    "....?B?B?..C....C......................................................................",
    "....B...B...............................................................................",
    "........................................................................................",
    ".............G..........................................................................",
    ".....................P2...........................P3............................F..........",
    "........................................................................................",
    "........................................................................................",
    "........................................................................................",
    "#..#####################....###############.....#################.....###################",
    "########################################################################################",
]

def generate_world(level_data):
    platforms = []
    coins = []
    enemies = []
    pipes = []
    flag = None

    for y, row in enumerate(level_data):
        for x, tile in enumerate(row):
            pos_x = x * TILE_SIZE
            pos_y = y * TILE_SIZE
            if tile == '#':
                platforms.append(Platform(pos_x, pos_y, color=COLOR_GROUND))
            elif tile == 'B':
                platforms.append(Platform(pos_x, pos_y, color=COLOR_BRICK))
            elif tile == '?':
                platforms.append(Platform(pos_x, pos_y, color=COLOR_QBLOCK))
            elif tile == 'C':
                coins.append(Coin(pos_x, pos_y))
            elif tile == 'G':
                enemies.append(Goomba(pos_x, pos_y))
            elif tile == 'P':
                height = int(row[x+1]) if x+1 < len(row) and row[x+1].isdigit() else 2
                pipes.append(Pipe(pos_x, pos_y, height))
            elif tile == 'F':
                flag = Flag(pos_x, pos_y)

    return platforms, coins, enemies, pipes, flag

# Generate World 1-1
platforms, coins, enemies, pipes, flag = generate_world(level_1_1)

# Entities
player = Player(TILE_SIZE * 2, SCREEN_HEIGHT - TILE_SIZE * 3)

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
    for enemy in enemies:
        enemy.update()

    # Coin Collection
    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            player.score += 100
            coins.remove(coin)

    # Enemy Collision
    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            if player.vy > 0 and player.rect.bottom > enemy.rect.top:
                enemies.remove(enemy)
                player.score += 200
                player.vy = -5  # Bounce
            else:
                player.respawn()

    # Win Condition
    if flag and player.rect.colliderect(flag.pole):
        print(f"LEVEL COMPLETE! SCORE: {player.score}")
        running = False

    # Scroll Camera (only rightward, SMB1 style)
    if player.rect.x > scroll_x + SCREEN_WIDTH // 2:
        scroll_x = player.rect.x - SCREEN_WIDTH // 2
    if scroll_x < 0:
        scroll_x = 0

    # Draw
    screen.fill(COLOR_BG)

    for p in platforms:
        pygame.draw.rect(screen, p.color, (p.rect.x - scroll_x, p.rect.y, p.rect.width, p.rect.height))
    for c in coins:
        pygame.draw.rect(screen, COLOR_COIN, (c.rect.x - scroll_x, c.rect.y, c.rect.width, c.rect.height))
    for e in enemies:
        pygame.draw.rect(screen, COLOR_GOOMBA, (e.rect.x - scroll_x, e.rect.y, e.rect.width, e.rect.height))
    for p in pipes:
        p.draw(screen, scroll_x)
    if flag:
        pygame.draw.rect(screen, COLOR_FLAGPOLE, (flag.pole.x - scroll_x, flag.pole.y, flag.pole.width, flag.pole.height))
        pygame.draw.rect(screen, COLOR_FLAG, (flag.flag.x - scroll_x, flag.flag.y, flag.flag.width, flag.flag.height))
    pygame.draw.rect(screen, COLOR_PLAYER, (player.rect.x - scroll_x, player.rect.y, player.rect.width, player.rect.height))

    # Score Display
    font = pygame.font.SysFont(None, 24)
    score_surf = font.render(f"Score: {player.score}", True, (255, 255, 255))
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
