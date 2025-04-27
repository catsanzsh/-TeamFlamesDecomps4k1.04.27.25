from ursina import *

# Initialize the Ursina app
app = Ursina()

# Player setup
player = Entity(model='cube', color=color.red, scale=(1, 1, 1), position=(0, 1, 0))
player_controller = FirstPersonController(model=player, jump_height=2, speed=5, gravity=1)

# Ground setup
ground = Entity(
    model='plane',
    scale=(100, 1, 100),
    color=color.green,
    texture='white_cube',
    texture_scale=(100, 100),
    collider='box'
)

# Platforms (inspired by Bob-omb Battlefield)
platforms = [
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(-10, 1, 10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 1, 5), position=(10, 1, -10), collider='box'),
    Entity(model='cube', color=color.blue, scale=(5, 2, 5), position=(0, 2, 15), collider='box')  # Higher platform
]

# Coins
coins = [
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(-5, 2, 5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(5, 2, -5), collider='sphere'),
    Entity(model='sphere', color=color.yellow, scale=0.5, position=(0, 3, 15), collider='sphere')
]

# Enemies (simple moving cubes)
enemies = [
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(15, 1, 15), collider='box'),
    Entity(model='cube', color=color.brown, scale=(1, 1, 1), position=(-15, 1, 15), collider='box')
]

# Star (objective)
star = Entity(model='sphere', color=color.gold, scale=1, position=(0, 5, 0), collider='sphere')

# Camera setup (third-person view)
camera.position = (0, 15, -30)
camera.look_at(player)

# Game variables
coin_count = 0

# Update function (game loop)
def update():
    global coin_count

    # Enemy movement (simple back-and-forth)
    for enemy in enemies:
        enemy.x += 0.05 * sin(time.time())  # Oscillating movement

    # Coin collection
    for coin in coins[:]:  # Copy list to allow removal
        if coin.enabled and distance(player, coin) < 1:
            coin.disable()
            coin_count += 1
            print(f"Coin collected! Total: {coin_count}")

    # Star collection
    if star.enabled and distance(player, star) < 1:
        star.disable()
        print("Star collected! Level complete!")

# Input handling (optional reset)
def input(key):
    if key == 'r':
        player.position = (0, 1, 0)  # Reset player position
        for coin in coins:
            coin.enable()  # Reset coins
        star.enable()  # Reset star
        global coin_count
        coin_count = 0
        print("Game reset!")

# Run the game
app.run()
