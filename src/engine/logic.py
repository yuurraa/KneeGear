import pygame
import random
from src.enemies import BasicEnemy, TankEnemy, SniperEnemy, ChargerEnemy
from src.player.pickups import HeartEffect
import src.engine.game_state as game_state
import src.engine.constants as constants


def update_projectiles():
    # Let the bullet pool handle updating all bullets
    game_state.bullet_pool.update()

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, game_state.screen_width)
        y = -20
    elif side == "bottom":
        x = random.randint(0, game_state.screen_width)
        y = game_state.screen_height + 20
    elif side == "left":
        x = -20
        y = random.randint(0, game_state.screen_height)
    else:  # "right"
        x = game_state.screen_width + 20
        y = random.randint(0, game_state.screen_height)

    # Use weighted random selection for enemy type
    enemy_types = [
        (BasicEnemy, 0.6),  
        (TankEnemy, 0.3),
        (ChargerEnemy, 0.2),
        (SniperEnemy, 0.2)    
    ]
    
    EnemyClass = random.choices(
        population=[enemy_type for enemy_type, _ in enemy_types],
        weights=[weight for _, weight in enemy_types],
        k=1
    )[0]
    
    enemy = EnemyClass(x, y, game_state.enemy_scaling)
    game_state.enemies.append(enemy)


def spawn_heart():
    # Use the player's max pickups to limit hearts
    if len(game_state.hearts) < game_state.player.max_pickups_on_screen:
        x = random.randint(25, game_state.screen_width - 25)
        y = random.randint(25, game_state.screen_height - 25)
        # Create a HeartEffect object at (x, y)
        heart = HeartEffect((x, y), constants.PINK, particle_count=20)
        game_state.hearts.append(heart)

def update_hearts():
    # Iterate over a copy since we might remove hearts
    for heart in game_state.hearts[:]:
        # Create a rectangle around the heart's position for collision detection.
        # Adjust the size as needed; here we use a 20x20 box centered on heart.pos.
        heart_rect = pygame.Rect(heart.pos[0] - 10, heart.pos[1] - 10, 20, 20)
        player_rect = pygame.Rect(game_state.player.x - 15, game_state.player.y - 15, 30, 30)
        
        if player_rect.colliderect(heart_rect):
            heal_amount = game_state.player.heal_from_pickup()
            # Add a healing number effect
            game_state.damage_numbers.append({
                "x": game_state.player.x,
                "y": game_state.player.y,
                "value": heal_amount,
                "timer": 60,
                "color": constants.GREEN
            })
            # Remove the heart once it's picked up
            game_state.hearts.remove(heart)

def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()

    # Handle movement
    game_state.player.update(keys)

    # Handle skin change (for example, pressing '1' for default and '2' for pentagon)
    if keys[pygame.K_1]:
        game_state.player.change_skin(0)  # Change to square skin
    elif keys[pygame.K_2]:
        game_state.player.change_skin(1)  # Change to pentagon skin

    # Handle shooting
    if mouse_pressed[0] and not game_state.game_over:
        game_state.player.shoot_regular(pygame.mouse.get_pos())

    if mouse_pressed[2] and not game_state.game_over:
        game_state.player.shoot_special(pygame.mouse.get_pos())

    return keys


def update_enemies():
    # current_tick = game_state.in_game_ticks_elapsed  
    for enemy in game_state.enemies[:]:
        enemy.update(game_state.player.x, game_state.player.y, game_state)
