import pygame
import random
from src.player.pickups import HeartEffect
import src.engine.game_state as game_state
import src.engine.constants as constants


def update_projectiles():
    # Let the bullet pool handle updating all bullets
    game_state.bullet_pool.update()

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

def calculate_enemy_scaling(elapsed_seconds):
    scaling_factor = 2.02 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor


def calculate_wave_spawn_interval(elapsed_seconds):
    spawn_interval = constants.base_wave_interval * (2 ** (-elapsed_seconds / constants.wave_spawn_rate_doubling_time_seconds))
    return max(0.5, spawn_interval)
