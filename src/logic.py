import pygame
import math
import random
from src.helpers import calculate_angle
from src.projectiles import Alignment
from src.enemies import BasicEnemy, TankEnemy, SniperEnemy, ChargerEnemy

import src.game_state as game_state
import src.constants as constants


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
    if len(game_state.hearts) < game_state.player.max_pickups_on_screen:
        game_state.hearts.append([
            random.randint(25, game_state.screen_width - 25),
            random.randint(25, game_state.screen_height - 25)
        ])


def update_hearts():
    for heart in game_state.hearts[:]:
        if pygame.Rect(game_state.player.x - 15, game_state.player.y - 15, 30, 30).colliderect(pygame.Rect(heart[0] - 10, heart[1] - 10, 20, 20)):
            heal_amount = game_state.player.heal_from_pickup()
            
            # Add healing number
            game_state.damage_numbers.append({
                "x": game_state.player.x,
                "y": game_state.player.y,
                "value": heal_amount,
                "timer": 60,
                "color": constants.GREEN
            })
            
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
