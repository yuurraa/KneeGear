import pygame
import math
import random
import game_state
import constants
import score
from helpers import calculate_angle


def handle_player_movement(keys):
    x, y = game_state.player_x, game_state.player_y

    if keys[pygame.K_w]:
        y -= constants.player_speed
    if keys[pygame.K_s]:
        y += constants.player_speed
    if keys[pygame.K_a]:
        x -= constants.player_speed
    if keys[pygame.K_d]:
        x += constants.player_speed

    # Restrict player to screen boundaries
    x = max(15, min(x, game_state.screen_width - 15))
    y = max(15, min(y, game_state.screen_height - 15))

    game_state.player_x = x
    game_state.player_y = y


def move_enemy(enemy, target_x, target_y):
    speed = constants.tank_speed if enemy["type"] == "tank" else constants.enemy_speed
    angle = math.radians(calculate_angle(enemy["x"], enemy["y"], target_x, target_y))
    enemy["x"] += speed * math.cos(angle)
    enemy["y"] += speed * math.sin(angle)

    # Restrict enemies to screen boundaries
    enemy["x"] = max(20, min(enemy["x"], game_state.screen_width - 20))
    enemy["y"] = max(20, min(enemy["y"], game_state.screen_height - 20))


def update_projectiles():
    for bullet in game_state.projectiles[:]:
        # Regular bullet movement
        if len(bullet) <= 3 or bullet[3] != "special":
            bullet[0] += constants.player_bullet_speed * math.cos(math.radians(bullet[2]))
            bullet[1] += constants.player_bullet_speed * math.sin(math.radians(bullet[2]))
        # Special shot movement (faster, more damage, and piercing)
        if len(bullet) > 3 and bullet[3] == "special":
            bullet[0] += (constants.player_special_bullet_speed) * math.cos(math.radians(bullet[2]))
            bullet[1] += (constants.player_special_bullet_speed) * math.sin(math.radians(bullet[2]))

        hit_enemy = False
        for enemy in game_state.enemies[:]:
            # Check collision with the enemy
            if (enemy["health"] > 0 and
                pygame.Rect(enemy["x"] - 20, enemy["y"] - 20, 40, 40).colliderect(pygame.Rect(bullet[0] - 10, bullet[1] - 10, 20, 20))):

                damage = 20 if (len(bullet) > 3 and bullet[3] == "special") else 10
                enemy["health"] -= damage

                # Add damage number at enemy's position
                game_state.damage_numbers.append({
                    "x": enemy["x"],
                    "y": enemy["y"],
                    "value": damage,
                    "timer": 60,  # Frames the number will be displayed
                    "color": constants.RED  # Color for enemy damage
                })

                if enemy["health"] <= 0:
                    score.handle_enemy_killed(enemy["type"])  # Update score when enemy is killed
                    game_state.enemies.remove(enemy)

                if damage == 10:
                    hit_enemy = True  # Regular bullets should be removed after the first hit

        # Remove regular bullet after hitting one enemy
        if hit_enemy and (len(bullet) <= 3 or bullet[3] != "special"):
            game_state.projectiles.remove(bullet)
            continue

        # Remove bullets outside the screen
        if (bullet[0] < 0 or bullet[0] > game_state.screen_width or
            bullet[1] < 0 or bullet[1] > game_state.screen_height):
            if bullet in game_state.projectiles:
                game_state.projectiles.remove(bullet)


def update_enemy_bullets():
    current_time = pygame.time.get_ticks() / 1000.0

    for bullet in game_state.enemy_bullets[:]:
        time_since_homing = current_time - bullet[3]

        # Within homing duration
        if time_since_homing < 1:
            angle_to_player = calculate_angle(bullet[0], bullet[1], game_state.player_x, game_state.player_y)
            angle_diff = angle_to_player - bullet[2]

            # Normalize angle difference
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360

            # Limit turn angle
            if abs(angle_diff) > constants.max_turn_angle:
                angle_diff = constants.max_turn_angle if angle_diff > 0 else -constants.max_turn_angle

            bullet[2] += angle_diff

        # Move bullet
        bullet[0] += constants.enemy_homing_bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += constants.enemy_homing_bullet_speed * math.sin(math.radians(bullet[2]))

        # Check collision with player
        if pygame.Rect(game_state.player_x - 15, game_state.player_y - 15, 30, 30).colliderect(pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10)):
            game_state.player_health -= 10

            # Add damage number at player's position
            game_state.damage_numbers.append({
                "x": game_state.player_x,
                "y": game_state.player_y,
                "value": 10,
                "timer": 60,
                "color": constants.YELLOW  # Color for player damage
            })

            game_state.enemy_bullets.remove(bullet)
            continue

        # Remove bullets outside screen
        if (bullet[0] < 0 or bullet[0] > game_state.screen_width or
            bullet[1] < 0 or bullet[1] > game_state.screen_height):
            game_state.enemy_bullets.remove(bullet)


def update_enemy_aoe_bullets():
    for bullet in game_state.enemy_aoe_bullets[:]:
        bullet[0] += constants.enemy_aoe_bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += constants.enemy_aoe_bullet_speed * math.sin(math.radians(bullet[2]))

        # Check collision with player
        if pygame.Rect(game_state.player_x - 15, game_state.player_y - 15, 30, 30).colliderect(pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10)):
            game_state.player_health -= 5

            # Add damage number at player's position
            game_state.damage_numbers.append({
                "x": game_state.player_x,
                "y": game_state.player_y,
                "value": 5,
                "timer": 60,
                "color": constants.YELLOW
            })

            game_state.enemy_aoe_bullets.remove(bullet)
            continue

        # Remove bullets outside screen
        if (bullet[0] < 0 or bullet[0] > game_state.screen_width or
            bullet[1] < 0 or bullet[1] > game_state.screen_height):
            game_state.enemy_aoe_bullets.remove(bullet)


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
        game_state.enemies.append({
            "x": x,
            "y": y,
            "health": 400,
            "last_shot_time": 0,
            "last_aoe_time": 0,
            "type": "tank",
            "last_shotgun_time": 0
        })
    else:
        game_state.enemies.append({
            "x": x,
            "y": y,
            "health": 100,
            "last_shot_time": 0,
            "last_aoe_time": 0,
            "type": "regular"
        })


def enemy_homing_shoot(enemy, target_x, target_y):
    current_time = pygame.time.get_ticks() / 1000.0
    if current_time - enemy["last_shot_time"] >= constants.enemy_homing_interval:
        angle = calculate_angle(enemy["x"], enemy["y"], target_x, target_y)
        game_state.enemy_bullets.append([enemy["x"], enemy["y"], angle, current_time])
        enemy["last_shot_time"] = current_time


def enemy_aoe_shoot(enemy):
    current_time = pygame.time.get_ticks() / 1000.0
    if current_time - enemy["last_aoe_time"] >= constants.enemy_aoe_interval:
        for angle in range(0, 360, 45):
            game_state.enemy_aoe_bullets.append([enemy["x"], enemy["y"], angle])
        enemy["last_aoe_time"] = current_time


def tank_shotgun(enemy, target_x, target_y):
    current_time = pygame.time.get_ticks() / 1000.0
    if current_time - enemy.get("last_shotgun_time", 0) >= constants.tank_shotgun_interval:
        base_angle = calculate_angle(enemy["x"], enemy["y"], target_x, target_y)
        for _ in range(constants.tank_shotgun_pellet_count):
            angle = base_angle + random.uniform(-constants.tank_shotgun_spread, constants.tank_shotgun_spread)
            speed = random.uniform(*constants.tank_pellet_speed_range)
            game_state.tank_pellets.append([enemy["x"], enemy["y"], angle, speed])
        enemy["last_shotgun_time"] = current_time


def update_tank_pellets():
    for pellet in game_state.tank_pellets[:]:
        pellet[0] += pellet[3] * math.cos(math.radians(pellet[2]))
        pellet[1] += pellet[3] * math.sin(math.radians(pellet[2]))

        # Check collision with player
        if pygame.Rect(game_state.player_x - 15, game_state.player_y - 15, 30, 30).colliderect(pygame.Rect(pellet[0] - 3, pellet[1] - 3, 6, 6)):
            game_state.player_health -= 3

            # Add damage number at player's position
            game_state.damage_numbers.append({
                "x": game_state.player_x,
                "y": game_state.player_y,
                "value": 3,
                "timer": 60,
                "color": constants.YELLOW
            })

            game_state.tank_pellets.remove(pellet)
            continue

        # Remove pellets outside screen
        if (pellet[0] < 0 or pellet[0] > game_state.screen_width or
            pellet[1] < 0 or pellet[1] > game_state.screen_height):
            game_state.tank_pellets.remove(pellet)



def spawn_heart():
    if len(game_state.hearts) < 1:
        game_state.hearts.append([
            random.randint(20, game_state.screen_width - 20),
            random.randint(20, game_state.screen_height - 20)
        ])


def update_hearts():
    for heart in game_state.hearts[:]:
        if pygame.Rect(game_state.player_x - 15, game_state.player_y - 15, 30, 30).colliderect(pygame.Rect(heart[0] - 10, heart[1] - 10, 20, 20)):
            heal_amount = min(20, 100 - game_state.player_health)
            game_state.player_health = min(game_state.player_health + 20, 100)
            
            # Add healing number
            game_state.damage_numbers.append({
                "x": game_state.player_x,
                "y": game_state.player_y,
                "value": heal_amount,
                "timer": 60,
                "color": constants.GREEN
            })
            
            game_state.hearts.remove(heart)

# logic.py
def handle_input():
    keys = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()
    current_time = pygame.time.get_ticks() / 1000.0

    # Left-click for a regular shot
    if (mouse_pressed[0] and
        not game_state.game_over and
        current_time - game_state.last_shot_time >= game_state.shoot_cooldown):
        mx, my = pygame.mouse.get_pos()
        angle = calculate_angle(game_state.player_x, game_state.player_y, mx, my)
        game_state.projectiles.append([game_state.player_x, game_state.player_y, angle])
        game_state.last_shot_time = current_time

    # Right-click for a special shot
    if (mouse_pressed[2] and
        not game_state.game_over and
        current_time - game_state.last_special_shot_time >= game_state.special_shot_cooldown):
        mx, my = pygame.mouse.get_pos()
        angle = calculate_angle(game_state.player_x, game_state.player_y, mx, my)
        game_state.projectiles.append([game_state.player_x, game_state.player_y, angle, "special"])
        game_state.last_special_shot_time = current_time

    # Calculate cooldown progress for skill icons
    left_click_cooldown_progress = max(0, (current_time - game_state.last_shot_time) / game_state.shoot_cooldown)
    right_click_cooldown_progress = max(0, (current_time - game_state.last_special_shot_time) / game_state.special_shot_cooldown)

    return keys, left_click_cooldown_progress, right_click_cooldown_progress


def update_enemies():
    for enemy in game_state.enemies[:]:
        move_enemy(enemy, game_state.player_x, game_state.player_y)
        if enemy["type"] == "tank":
            tank_shotgun(enemy, game_state.player_x, game_state.player_y)
        else:
            enemy_homing_shoot(enemy, game_state.player_x, game_state.player_y)
            enemy_aoe_shoot(enemy)

        if enemy["health"] <= 0:
            game_state.enemies.remove(enemy)
