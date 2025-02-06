import pygame
import math
import random
from src.helpers import calculate_angle
from src.projectiles import Alignment
from src.enemies import BasicEnemy, TankEnemy, SniperEnemy, ChargerEnemy

import src.game_state as game_state
import src.constants as constants

def move_enemy(enemy, target_x, target_y):
    # Determine base speed from constants; then scale it so that movement is consistent.
    base_speed = (constants.tank_speed if enemy.type == "tank" else constants.basic_enemy_speed)
    speed = base_speed * game_state.scale  # Scale the movement speed

    angle = math.radians(calculate_angle(enemy.x, enemy.y, target_x, target_y))
    enemy.x += speed * math.cos(angle)
    enemy.y += speed * math.sin(angle)

    # Adjust boundaries so that they are in scaled coordinates.
    min_bound = 20 * game_state.scale
    max_x = game_state.screen_width * game_state.scale - min_bound
    max_y = game_state.screen_height * game_state.scale - min_bound - (constants.experience_bar_height * game_state.scale)
    enemy.x = max(min_bound, min(enemy.x, max_x))
    enemy.y = max(min_bound, min(enemy.y, max_y))


def update_projectiles():
    # Update all projectiles
    for bullet in game_state.projectiles[:]:
        # Update special bullet behaviors
        bullet.update()


def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, game_state.screen_width) * game_state.scale
        y = -20 * game_state.scale
    elif side == "bottom":
        x = random.randint(0, game_state.screen_width) * game_state.scale
        y = (game_state.screen_height + 20) * game_state.scale
    elif side == "left":
        x = -20 * game_state.scale
        y = random.randint(0, game_state.screen_height) * game_state.scale
    else:  # "right"
        x = (game_state.screen_width + 20) * game_state.scale
        y = random.randint(0, game_state.screen_height) * game_state.scale

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
        # The random positions are generated in base space then scaled.
        x = random.randint(20, game_state.screen_width - 20) * game_state.scale
        y = random.randint(20, game_state.screen_height - 20) * game_state.scale
        game_state.hearts.append([x, y])


def update_hearts():
    for heart in game_state.hearts[:]:
        # Build rectangles in scaled coordinates.
        player_rect = pygame.Rect(
            game_state.player.x - (15 * game_state.scale),
            game_state.player.y - (15 * game_state.scale),
            30 * game_state.scale,
            30 * game_state.scale
        )
        heart_rect = pygame.Rect(
            heart[0] - (10 * game_state.scale),
            heart[1] - (10 * game_state.scale),
            20 * game_state.scale,
            20 * game_state.scale
        )
        if player_rect.colliderect(heart_rect):
            heal_amount = game_state.player.heal_from_pickup()
            
            # Add healing number (positions are assumed to be stored in scaled coordinates)
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
    # Update each enemy using the player's (scaled) coordinates.
    for enemy in game_state.enemies[:]:
        enemy.update(game_state.player.x, game_state.player.y, game_state)
