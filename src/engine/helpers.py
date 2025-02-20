import math
import pygame
import os
import json
import random
import time

import src.engine.game_state as game_state
import src.engine.constants as constants

def calculate_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def reset_game():
    from src.enemies.enemy_pool import EnemyPool
    enemy_pool = EnemyPool()
    random.seed(time.time())
    game_state.player.reset()
    if hasattr(game_state, 'current_upgrade_buttons'):
        delattr(game_state, 'current_upgrade_buttons')
    if hasattr(game_state, 'final_time'):
        delattr(game_state, 'final_time')
    game_state.enemies.clear()
    game_state.projectiles.clear()
    game_state.hearts.clear()
    game_state.damage_numbers.clear()
    game_state.experience_updates.clear()
    for bullet in game_state.bullet_pool.pool:
        bullet.deactivate()
    game_state.player.upgrade_levels = {}
    game_state.enemy_scaling = 1
    game_state.fade_alpha = 0
    game_state.game_over = False
    game_state.start_time_ms = pygame.time.get_ticks()
    game_state.in_game_ticks_elapsed = 0
    game_state.last_wave_time = -999  # Reset enemy spawn timer   
    game_state.wave_active = False
    game_state.wave_enemies_spawned = 0
    game_state.next_enemy_spawn_time = 0
    game_state.first_enemy_spawned = False  # Reset first enemy spawn flag
    import src.engine.score as score
    score.reset_score()
    game_state.player.x = game_state.screen_width // 2
    game_state.player.y = game_state.screen_height // 2
    game_state.notification_visible = False
    game_state.notification_message = ""
    game_state.notification_queue = []
    game_state.paused = False
    
def load_music_settings():
    """Load music settings from a file."""
    try:
        if not os.path.exists("data/settings.txt"):
            save_music_settings(constants.music_volume)

        with open("data/settings.txt", "r") as file:
            volume_line = file.readline().strip()
            volume = float(volume_line)
            return max(0.0, min(1.0, volume))
    except Exception as e:
        print(f"Error loading settings: {e}")
        return constants.music_volume

def save_music_settings(volume):
    """Save music settings to a file."""
    try:
        with open("data/settings.txt", "w") as file:
            file.write(f"{volume}\n")
    except Exception as e:
        print(f"Error saving settings: {e}")
    
def get_design_mouse_pos(mouse_pos):
    """
    Convert a mouse position from screen coordinates to design coordinates.
    """
    scale_x = game_state.screen_width / game_state.screen_width
    scale_y = game_state.screen_height / game_state.screen_height
    return (int(mouse_pos[0] * scale_x), int(mouse_pos[1] * scale_y))

def get_ui_scaling_factor():
    return game_state.screen_width / game_state.screen_width

def get_text_scaling_factor(font_size):
    return round(font_size * (game_state.screen_width / game_state.screen_width))
      
def fade_to_black(surface, wait_time=5, step=20):
    """
    Assumes that 'surface' already has the current scene drawn.
    Gradually overlays a black surface (alpha increases from 0 to 255)
    to fade the scene out.
    """
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill((0, 0, 0))
    for alpha in range(0, 256, step):
        overlay.set_alpha(alpha)
        temp_surface = surface.copy()
        temp_surface.blit(overlay, (0, 0))
        pygame.display.flip()
        # pygame.time.wait(wait_time)
    # Final update: ensure the screen is completely black.
    black_surface = pygame.Surface((game_state.screen_width, game_state.screen_height))
    black_surface.fill((0, 0, 0))
    pygame.display.flip()

def fade_from_black_step(surface, step=5):
    """
    Fades one step from black by decreasing the alpha.
    Should be called once per frame.
    Returns the updated alpha value.
    """
    game_state.fade_alpha = max(game_state.fade_alpha - step, 0)
    
    # Create an overlay the same size as the surface.
    overlay = pygame.Surface(surface.get_size())
    overlay.fill((0, 0, 0))
    overlay.set_alpha(game_state.fade_alpha)
    
    # Draw the overlay on top of the current scene.
    surface.blit(overlay, (0, 0))
    
    return game_state.fade_alpha

def save_skin_selection():
    with open("data/skin_selection.json", "w") as f:
        json.dump({"current_skin_id": game_state.player.current_skin_id}, f)
    print(f"Saved skin ID: {game_state.player.current_skin_id}")  # Debug

def load_skin_selection():
    if os.path.exists("data/skin_selection.json"):
        with open("data/skin_selection.json", "r") as f:
            data = json.load(f)
            skin_id = data.get("current_skin_id", "default")
            print(f"Loaded skin ID: {skin_id}")  # Debug
            game_state.player.change_skin(skin_id)
            
def queue_notification(message):
    import src.engine.game_state as game_state
    # Each notification is a dict with a message and a timer.
    game_state.notifications.append({
        "message": message,
        "timer": game_state.notification_total_duration,
        # Optionally, you can include other data like a fixed y-position
        "y": 50  # for example, when fully visible
    })
