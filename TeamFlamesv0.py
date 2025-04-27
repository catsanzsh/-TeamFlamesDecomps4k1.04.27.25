from ursina import *
from math import sin, degrees, atan2

# Initialize the Ursina app
app = Ursina()

# Player setup
player = Entity(
    model='cube',           # Placeholder; consider a character model later
    color=color.red,
    scale=(1, 1, 1),
    position=(0, 1, 0),
    collider='box'
)
player.velocity_y = 0       # Vertical velocity for jumping
player.is_on_ground = False # Flag to track ground state

# Ground setup with a simple hill-like ramp
ground = Entity(
    model='plane',
    scale=(100, 1, 100),
    color=color.green,
    texture='white_cube',
    texture_scale=(100, 100),
    collider='box'
)
ramp = Entity(
    model='cube',
    scale=(10, 1, 10),
    position=(20, 0, 20),
    rotation=(0, 0, 15),    # Sloped like a hill
    color=color.green,
    collider='box'
)

# Platforms inspired by Bob-omb Battlefield
platforms = [
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(-10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(10, 1, -10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 2, 5), position=(0, 2, 15), collider='box'),  # Higher platform
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(20, 1, 20), collider='box')   # Near ramp
]

# Moving platform (dynamic element)
moving_platform = Entity(
    model='cube',
    color=color.cyan,
    scale=(5, 1, 5),
    position=(15, 1, 0),
    collider='box'
)
moving_platform.animate_x(20, duration=2, loop=True)
moving_platform.animate_x(15, duration=2, delay=2, loop=True)

# Coins
coins = [
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(-5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(5, 2, -5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(0, 3, 15), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(17, 2, 20), collider='sphere')  # On ramp
]

# Enemies (Bob-omb-like behavior)
enemies = [
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(15, 1, 15), collider='box'),
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(-15, 1, 15), collider='box')
]
for enemy in enemies:
    enemy.animate_x(enemy.x + 5, duration=3, loop=True)
    enemy.animate_x(enemy.x, duration=3, delay=3, loop=True)

# Star (objective)
star = Entity(
    model='sphere',
    color=color.gold,
    scale=1,
    position=(0, 5, 0),     # Central, elevated position
    collider='sphere'
)

# UI elements
coin_count = 0
coin_text = Text(text=f'Coins: {coin_count}', position=(-0.85, 0.45), scale=2)

# Skybox for SM64-like background
Sky(texture='sky_sunset')   # Optional: use a custom skybox texture

# Camera setup (third-person)
camera.z = -10              # Initial offset; updated dynamically

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
            player.velocity_y = 5   # Jump height
    else:
        player.is_on_ground = False
        player.velocity_y -= 9.8 * time.dt  # Gravity
    player.y += player.velocity_y * time.dt

    # Camera follows player from behind
    camera.position = player.position - player.forward * 10 + Vec3(0, 5, 0)
    camera.look_at(player)

    # Coin animation and collection
    for coin in coins[:]:
        if coin.enabled:
            coin.rotation_y += 100 * time.dt    # Spin effect
            if distance(player, coin) < 1:
                coin.disable()
                coin_count += 1
                coin_text.text = f'Coins: {coin_count}'
                print(f"Coin collected! Total: {coin_count}")

    # Star animation and collection
    if star.enabled:
        star.rotation_y += 50 * time.dt         # Spin effect
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
            print("Star collected! Level complete!")

    # Enemy collision
    for enemy in enemies:
        if player.intersects(enemy).hit:
            player.position = (0, 1, 0)
            player.velocity_y = 0
            print("Hit by enemy! Reset position.")

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
        print("Game reset!")

# Run the game
app.run()
