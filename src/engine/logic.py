import pygame
import random
from src.player.pickups import HeartEffect
import src.engine.game_state as game_state
import src.engine.constants as constants
from src.engine.helpers import get_ui_scaling_factor


def update_projectiles():
    # Let the bullet pool handle updating all bullets
    game_state.bullet_pool.update()

def spawn_heart():
    ui_zones = []
    ui_zones.append(pygame.Rect(20, 20, 300, 20))  # Health bar

    ui_scaling = get_ui_scaling_factor()  # Or use your existing ui_scaling_factor
    icon_size = 140 * ui_scaling
    padding = 20 * ui_scaling

    left_icon_rect = pygame.Rect(game_state.screen_width - icon_size - padding,
                                 padding + 120 * ui_scaling - 20 * ui_scaling,
                                 icon_size, icon_size)
    ui_zones.append(left_icon_rect)
    right_icon_rect = pygame.Rect(game_state.screen_width - icon_size - padding,
                                  padding + 120 * ui_scaling - 20 * ui_scaling + icon_size + padding,
                                  icon_size, icon_size)
    ui_zones.append(right_icon_rect)
    fps_rect = pygame.Rect(game_state.screen_width - 140 * ui_scaling - padding,
                           padding, 140 * ui_scaling, 30)
    ui_zones.append(fps_rect)
    
    # Add a UI zone for the score text
    score_rect = pygame.Rect(20, 55, 200, 40)  # Adjust width/height as needed
    ui_zones.append(score_rect)

    max_attempts = 1
    valid_position = None
    for _ in range(max_attempts):
        x = random.randint(25, game_state.screen_width - 25)
        y = random.randint(25, game_state.screen_height - 25)
        heart_rect = pygame.Rect(x - 10, y - 10, 20, 20)
        if not any(heart_rect.colliderect(ui_rect) for ui_rect in ui_zones):
            valid_position = (x, y)
            break

    if valid_position and len(game_state.hearts) < game_state.player.max_pickups_on_screen:
        heart = HeartEffect(valid_position, constants.PINK, particle_count=20)
        game_state.hearts.append(heart)
    # Otherwise, do nothing—no heart will spawn if a valid spot isn't found.

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
    scaling_factor = 1.98 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor


def calculate_wave_spawn_interval(elapsed_seconds):
    spawn_interval = constants.base_wave_interval * (2 ** (-elapsed_seconds / constants.wave_spawn_rate_doubling_time_seconds))
    return max(0.5, spawn_interval)
