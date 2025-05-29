from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from ursina.prefabs.health_bar import HealthBarwss

app = Ursina()

window.title = 'Call of Duty: Ursina Edition'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Player setup
player = FirstPersonController(
    model='cube',
    color=color.azure,
    origin_y=-.5,
    speed=7,
    collider='box',
    jump_height=2,
    jump_duration=0.4
)
player.health = 100
player.max_health = 100
player.ammo = 30
player.max_ammo = 30
player.reload_time = 1.5
player.reloading = False
player.shoot_cooldown = 0.1
player.last_shot = 0

# Gun model
gun = Entity(
    parent=camera.ui,
    model='cube',
    color=color.gray,
    scale=(0.3,0.15,1),
    position=(0.2,-0.2,0.5),
    rotation=(0,0,0)
)

# Health bar UI
health_bar = HealthBar(parent=camera.ui, position=window.top_left + Vec2(0.1, -0.1), color=color.red, max_value=player.max_health)
ammo_text = Text(text=f'Ammo: {player.ammo}/{player.max_ammo}', parent=camera.ui, position=window.top_right + Vec2(-0.2, -0.1), origin=(0,0), scale=1.5)

# Bullet list
bullets = []

# Enemy list
enemies = []

# Map (simple floor and some obstacles)
ground = Entity(model='plane', scale=(50,1,50), texture='white_cube', texture_scale=(50,50), collider='box', color=color.dark_gray)
for _ in range(10):
    Entity(model='cube', scale=(random.uniform(2,5),random.uniform(2,5),random.uniform(2,5)),
           position=(random.uniform(-20,20),1,random.uniform(-20,20)), color=color.light_gray, collider='box')

# Enemy spawn function
def spawn_enemy():
    x = random.uniform(-20, 20)
    z = random.uniform(-20, 20)
    enemy = Entity(model='cube', color=color.red, scale=(1,2,1), position=(x,1,z), collider='box')
    enemy.health = 50
    enemy.max_health = 50
    enemy.health_bar = HealthBar(parent=enemy, y=1.5, max_value=enemy.max_health, value=enemy.health, scale=(1.5,0.1))
    enemies.append(enemy)

# Spawn 10 enemies at start
for _ in range(10):
    spawn_enemy()

def shoot():
    if player.reloading or time.time() - player.last_shot < player.shoot_cooldown or player.ammo <= 0:
        return
    player.last_shot = time.time()
    player.ammo -= 1
    # Muzzle flash
    gun.color = color.yellow
    invoke(setattr, gun, 'color', color.gray, delay=0.05)
    # Raycast for instant hit
    hit_info = raycast(camera.world_position, camera.forward, distance=50, ignore=(player,))
    if hit_info.hit and hit_info.entity in enemies:
        hit_info.entity.health -= 25
        hit_info.entity.health_bar.value = hit_info.entity.health
        if hit_info.entity.health <= 0:
            enemies.remove(hit_info.entity)
            destroy(hit_info.entity)
    # Play sound (optional)
    # Audio('shoot.wav')

def reload():
    if not player.reloading and player.ammo < player.max_ammo:
        player.reloading = True
        ammo_text.text = "Reloading..."
        invoke(reload_complete, delay=player.reload_time)

def reload_complete():
    player.ammo = player.max_ammo
    player.reloading = False

def update():
    if player.health <= 0:
        print("You died! Game Over.")
        application.quit()

    # Enemies chase and attack player
    for enemy in enemies:
        if distance(player.position, enemy.position) > 2:
            direction = (player.position - enemy.position).normalized()
            enemy.position += direction * 2 * time.dt
        else:
            player.health -= 10 * time.dt
        enemy.health_bar.value = enemy.health

    # Update UI
    health_bar.value = player.health
    ammo_text.text = f'Ammo: {int(player.ammo)}/{player.max_ammo}' if not player.reloading else "Reloading..."

    # Respawn enemies if all dead
    if not enemies:
        for _ in range(10):
            spawn_enemy()

def input(key):
    if key == 'left mouse down':
        shoot()
    if key == 'r':
        reload()

app.run()
from ursina import *
from ursina.prefabs.health_bar import HealthBar
import random
import math
from ursina.prefabs.health_bar import HealthBar
import random

app = Ursina()

# Player setup
player = Entity(model='cube', color=color.azure, scale=(1,2,1), collider='box')
player.speed = 5
player.health = 100
player.max_health = 100
player.ammo = 10
player.max_ammo = 10
player.reload_time = 2
player.reloading = False

# Camera setup
camera.parent = player
camera.position = (0,1.5,-4)
camera.rotation = (0,0,0)

# Health bar UI
health_bar = HealthBar(parent=camera.ui, position=window.top_left + Vec2(0.1, -0.1), color=color.red, max_value=player.max_health)
ammo_text = Text(text=f'Ammo: {player.ammo}/{player.max_ammo}', parent=camera.ui, position=window.top_right + Vec2(-0.2, -0.1), origin=(0,0))

# Bullet list
bullets = []

# Enemy list
enemies = []

# Enemy spawn function
def spawn_enemy():
    x = random.uniform(-20, 20)
    z = random.uniform(-20, 20)
    enemy = Entity(model='cube', color=color.red, scale=(1,2,1), position=(x,0,z), collider='box')
    enemy.health = 30
    enemies.append(enemy)

# Spawn 5 enemies at start
for _ in range(5):
    spawn_enemy()

def update():
    if player.health <= 0:
        print("You died! Game Over.")
        application.quit()

    # Player movement
    direction = Vec3(
        held_keys['d'] - held_keys['a'],
        0,
        held_keys['w'] - held_keys['s']
    ).normalized()
    player.position += player.forward * direction.z * player.speed * time.dt
    player.position += player.right * direction.x * player.speed * time.dt

    # Mouse look
    player.rotation_y += mouse.velocity[0] * 40
    camera.rotation_x -= mouse.velocity[1] * 40
    camera.rotation_x = clamp(camera.rotation_x, -90, 90)

    # Move bullets forward & check collision
    for bullet in bullets:
        bullet.position += bullet.forward * 40 * time.dt
        hit_info = bullet.intersects()
        if hit_info.hit:
            if hit_info.entity in enemies:
                hit_info.entity.health -= 10
                if hit_info.entity.health <= 0:
                    enemies.remove(hit_info.entity)
                    destroy(hit_info.entity)
            bullets.remove(bullet)
            destroy(bullet)
            continue
        # Remove bullet if too far
        if distance(bullet.position, player.position) > 50:
            bullets.remove(bullet)
            destroy(bullet)

    # Enemies chase player
    for enemy in enemies:
        direction = player.position - enemy.position
        if direction.length() > 1:
            enemy.position += direction.normalized() * 3 * time.dt
        else:
            # Enemy attacks player
            player.health -= 10 * time.dt
        if enemy.health <= 0:
            enemies.remove(enemy)
            destroy(enemy)

    # Update UI
    health_bar.value = player.health
    ammo_text.text = f'Ammo: {int(player.ammo)}/{player.max_ammo}'

bullets = []

def shoot():
    bullet = Entity(
        model='sphere',
        color=color.red,
        scale=0.2,
        position=player.position + player.forward,
    )
    bullet.rotation = player.rotation
    bullet.speed = 10
    bullets.append(bullet)

def update():
    for bullet in bullets:
        bullet.position += bullet.forward * bullet.speed * time.dt
        # optional: remove bullet if too far away or after some time



def reload():
    if not player.reloading and player.ammo < player.max_ammo:
        player.reloading = True
        print("Reloading...")
        invoke(reload_complete, delay=player.reload_time)

def reload_complete():
    player.ammo = player.max_ammo
    player.reloading = False
    print("Reloaded!")

def input(key):
    if key == 'left mouse down':
        shoot()
    if key == 'r':
        reload()

app.run()
