from ursina import *
from math import sin, atan2, degrees

# Initialize Ursina app
app = Ursina()
window.title = 'SM64-Inspired Platformer'

# Player setup
player = Entity(
    model='cube',           # Simple cube as player
    color=color.red,        # Mario-like color
    scale=(1, 1, 1),
    position=(0, 1, 0),
    collider='box'
)
player.velocity_y = 0       # For jumping mechanics
player.is_on_ground = False # Tracks if player is grounded

# Environment setup
ground = Entity(
    model='plane',
    scale=(100, 1, 100),
    color=color.green,
    collider='box'
)
ramp = Entity(
    model='cube',
    scale=(10, 1, 10),
    position=(20, 0, 20),
    rotation=(0, 0, 15),    # Sloped ramp
    color=color.green,
    collider='box'
)

# Platforms
platforms = [
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(-10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(0, 2, 15), collider='box'),
]

# Moving platform
moving_platform = Entity(
    model='cube',
    color=color.cyan,
    scale=(5, 1, 5),
    position=(15, 1, 0),
    collider='box'
)
moving_platform.animate_x(20, duration=2, loop=True)
moving_platform.animate_x(15, duration=2, delay=2, loop=True)

# Collectibles
coins = [
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(-5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(0, 3, 15), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(17, 2, 20), collider='sphere'),
]
star = Entity(
    model='sphere',
    color=color.gold,
    scale=1,
    position=(20, 5, 20),   # Atop the ramp
    collider='sphere'
)

# Enemies
enemies = [
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(10, 1, 10), collider='box'),
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(-10, 1, 10), collider='box'),
]
for enemy in enemies:
    enemy.animate_x(enemy.x + 5, duration=3, loop=True)
    enemy.animate_x(enemy.x, duration=3, delay=3, loop=True)

# UI
coin_count = 0
coin_text = Text(text=f'Coins: {coin_count}', position=(-0.85, 0.45), scale=2)

# Camera setup
camera.z = -10  # Initial offset

# Easter egg: Tribute to sm64decomp
hidden_platform = Entity(
    model='cube',
    scale=(3, 1, 3),
    position=(25, 3, 25),
    color=color.orange,
    collider='box'
)
sign = Entity(
    model='quad',
    color=color.white,
    scale=(2, 1),
    position=(25, 4, 25),
    billboard=True
)
Text(
    text="Thanks sm64decomp!",
    parent=sign,
    scale=2,
    origin=(0, 0),
    color=color.black
)

# Game loop
def update():
    global coin_count

    # Player movement
    move_speed = 5
    move_dir = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()
    if move_dir.length() > 0:
        player.rotation_y = degrees(atan2(move_dir.x, move_dir.z))
        player.position += move_dir * move_speed * time.dt

    # Gravity and jumping
    hit_info = raycast(
        origin=player.position,
        direction=Vec3(0, -1, 0),
        distance=player.scale_y / 2 + 0.1,
        ignore=(player,)
    )
    if hit_info.hit:
        player.is_on_ground = True
        player.velocity_y = 0
        if held_keys['space']:
            player.velocity_y = 5
    else:
        player.is_on_ground = False
        player.velocity_y -= 9.8 * time.dt
    player.y += player.velocity_y * time.dt

    # Camera follows player
    camera.position = player.position - player.forward * 10 + Vec3(0, 5, 0)
    camera.look_at(player)

    # Coin collection
    for coin in coins[:]:
        if coin.enabled:
            coin.rotation_y += 100 * time.dt
            if distance(player, coin) < 1:
                coin.disable()
                coin_count += 1
                coin_text.text = f'Coins: {coin_count}'

    # Star collection
    if star.enabled:
        star.rotation_y += 50 * time.dt
        if distance(player, star) < 1:
            star.disable()
            win_text = Text(
                text="Level Complete!",
                position=(0, 0),
                scale=3,
                origin=(0, 0),
                background=True
            )
            invoke(destroy, win_text, delay=3)

    # Enemy interactions
    for enemy in enemies[:]:
        if enemy.enabled and player.intersects(enemy).hit:
            if player.y > enemy.y + 1:
                enemy.scale_y = 0.1
                invoke(enemy.disable, delay=0.5)
            else:
                player.position = (0, 1, 0)
                player.velocity_y = 0

# Input handling
def input(key):
    if key == 'r':
        player.position = (0, 1, 0)
        player.velocity_y = 0
        for coin in coins:
            coin.enable()
        star.enable()
        global coin_count
        coin_count = 0
        coin_text.text = f'Coins: {coin_count}'

# Lighting (procedural, no media)
DirectionalLight(shadows=True).look_at(Vec3(-1, -1, -1))
AmbientLight(color=color.rgba(100, 100, 100, 0.1))

# Run the game
app.run()
