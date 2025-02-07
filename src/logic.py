import pygame
import math
import random
from src.helpers import calculate_angle
from src.projectiles import Alignment
from src.enemies import BasicEnemy, TankEnemy, SniperEnemy, ChargerEnemy

import src.game_state as game_state
import src.constants as constants


def update_projectiles():
    # Update all projectiles
    for bullet in game_state.projectiles[:]:
        # Update special bullet behaviors
        bullet.update()

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, game_state.DESIGN_WIDTH)
        y = -20
    elif side == "bottom":
        x = random.randint(0, game_state.DESIGN_WIDTH)
        y = game_state.DESIGN_HEIGHT + 20
    elif side == "left":
        x = -20
        y = random.randint(0, game_state.DESIGN_HEIGHT)
    else:  # "right"
        x = game_state.DESIGN_WIDTH + 20
        y = random.randint(0, game_state.DESIGN_HEIGHT)

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
            random.randint(20, game_state.DESIGN_WIDTH - 20),
            random.randint(20, game_state.DESIGN_HEIGHT - 20)
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

    # Handle shooting: use the new shooting methods (which use the in-game tick counter)
    if mouse_pressed[0] and not game_state.game_over:
        bullets = game_state.player.shoot_regular(pygame.mouse.get_pos())
        if bullets:
            game_state.projectiles.extend(bullets)

    if mouse_pressed[2] and not game_state.game_over:
        bullets = game_state.player.shoot_special(pygame.mouse.get_pos())
        if bullets:
            game_state.projectiles.extend(bullets)

    return keys


def update_enemies():
    # current_tick = game_state.in_game_ticks_elapsed  
    for enemy in game_state.enemies[:]:
        enemy.update(game_state.player.x, game_state.player.y, game_state)
