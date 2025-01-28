import pygame
import math
import random
import game_state
import constants
from helpers import calculate_angle
from projectiles import Alignment
from enemies import RegularEnemy, TankEnemy


def move_enemy(enemy, target_x, target_y):
    speed = constants.tank_speed if enemy.type == "tank" else constants.basic_enemy_speed
    angle = math.radians(calculate_angle(enemy.x, enemy.y, target_x, target_y))
    enemy.x += speed * math.cos(angle)
    enemy.y += speed * math.sin(angle)

    # Restrict enemies to screen boundaries, accounting for experience bar
    enemy.x = max(20, min(enemy.x, game_state.screen_width - 20))
    # Add padding above experience bar
    enemy.y = max(20, min(enemy.y, game_state.screen_height - 20 - constants.experience_bar_height))


def update_projectiles():
    # Update all projectiles
    for bullet in game_state.projectiles[:]:
        # Update special bullet behaviors
        bullet.update()
        
        # if bullet.alignment == Alignment.PLAYER:
        #     hit_enemy = False
        #     for enemy in game_state.enemies[:]:
        #         if bullet.check_collision(enemy):
        #             if enemy.apply_damage(bullet.damage, game_state):
        #                 game_state.enemies.remove(enemy)
        #             elif bullet.damage == constants.player_basic_bullet_damage:  # Regular bullet
        #                 hit_enemy = True
            
        #     if hit_enemy or bullet.is_out_of_bounds():
        #         game_state.projectiles.remove(bullet)
        # else:  # Enemy bullet
        #     if bullet.check_collision(None) or bullet.is_out_of_bounds():
        #         game_state.projectiles.remove(bullet)


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

    # The comment says 20% chance, but original code used 50% probability:
    if random.random() < 0.3:
        enemy = TankEnemy(x, y, game_state.enemy_scaling)
    else:
        enemy = RegularEnemy(x, y, game_state.enemy_scaling)
    
    game_state.enemies.append(enemy)


def spawn_heart():
    if len(game_state.hearts) < 1:
        game_state.hearts.append([
            random.randint(20, game_state.screen_width - 20),
            random.randint(20, game_state.screen_height - 20)
        ])


def update_hearts():
    for heart in game_state.hearts[:]:
        if pygame.Rect(game_state.player.x - 15, game_state.player.y - 15, 30, 30).colliderect(pygame.Rect(heart[0] - 10, heart[1] - 10, 20, 20)):
            heal_amount = min(20, 100 - game_state.player.health)
            game_state.player.health = min(game_state.player.health + 20, 100)
            
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
    current_time = pygame.time.get_ticks() / 1000.0

    # Handle movement
    game_state.player.update(keys)

    # Handle shooting
    if mouse_pressed[0] and not game_state.game_over:
        bullet = game_state.player.shoot_regular(pygame.mouse.get_pos(), current_time)
        if bullet:
            game_state.projectiles.append(bullet)

    if mouse_pressed[2] and not game_state.game_over:
        bullet = game_state.player.shoot_special(pygame.mouse.get_pos(), current_time)
        if bullet:
            game_state.projectiles.append(bullet)

    # Get cooldown progress for UI
    return keys


def update_enemies():
    current_time = pygame.time.get_ticks() / 1000.0
    for enemy in game_state.enemies[:]:
        move_enemy(enemy, game_state.player.x, game_state.player.y)
        enemy.shoot(game_state.player.x, game_state.player.y, current_time, game_state)

        if enemy.health <= 0:
            game_state.enemies.remove(enemy)



