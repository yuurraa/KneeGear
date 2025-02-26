import math
import pygame
import os
import json
import random
import time

import src.engine.game_state as game_state
import numpy as np

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

def get_ui_scaling_factor():
    """
    Return a uniform scaling factor based on the design resolution.
    This uses the smaller scale (min of x and y) so that UI elements maintain their aspect ratio.
    """
    scale_x = game_state.screen_width / game_state.design_width
    scale_y = game_state.screen_height / game_state.design_height
    return min(scale_x, scale_y)

def get_text_scaling_factor(font_size):
    """
    Scale font size by multiplying with 3 * the UI scaling factor.
    This increases all font sizes by a multiple of 3.
    """
    return round(font_size * 1.4 * get_ui_scaling_factor())
      
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
    pygame.display.flip()
    
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

def get_settings_file_path():
    """Return the full path for the settings file in the base data folder."""
    return os.path.join("data", "settings.txt")

def load_settings():
    """
    Load settings from the settings file.
    Expected format (one per line): key: value
    Returns a dictionary of settings.
    """
    settings_file = get_settings_file_path()
    settings = {}
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            for line in f:
                if ':' in line:
                    key, val = line.split(":", 1)
                    settings[key.strip()] = val.strip()
    return settings

def save_settings(settings):
    """
    Save the settings dictionary to the settings file.
    Each setting is saved on its own line in the format: key: value
    """
    settings_file = get_settings_file_path()
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w") as f:
        for key, val in settings.items():
            f.write(f"{key}: {val}\n")
            
# New: uniform hover overlay function
def draw_hover_overlay(screen, rect):
    """Draw a translucent gray overlay over the given rect."""
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((100, 100, 100, 110))
    screen.blit(overlay, rect.topleft)
    
# Global caches
_grid_cache = {}          # For coordinate grids (both raw and normalized)
_shimmer_cache = {}       # For computed shimmer surfaces keyed by parameters
LOW_RES_FACTOR = 2

def get_coordinate_grids(width, height):
    """Cache raw coordinate grids for given dimensions."""
    key = ("raw", width, height)
    if key not in _grid_cache:
        x_grid, y_grid = np.meshgrid(np.arange(width), np.arange(height))
        _grid_cache[key] = (x_grid, y_grid)
    return _grid_cache[key]

def get_normalized_grid(width, height):
    """Return a precomputed normalized grid based on raw grids."""
    key = ("norm", width, height)
    if key not in _grid_cache:
        x_grid, y_grid = get_coordinate_grids(width, height)
        # Normalized so that each coordinate lies in [0,1]
        norm_grid = (x_grid / width + y_grid / height) / 2.0
        _grid_cache[key] = norm_grid
    return _grid_cache[key]

def quantize_phase(phase, step=0.025):
    """Quantize phase to reduce the number of unique surfaces computed."""
    return round(phase / step) * step

def compute_shimmer_surface_for_tab_icon(rarity_color, rarity, width, height, phase, surface=None):
    # Determine low resolution dimensions
    low_width, low_height = width // LOW_RES_FACTOR, height // LOW_RES_FACTOR

    # Optional: create a cache key based on parameters (including quantized phase)
    q_phase = quantize_phase(phase)
    cache_key = (rarity_color, rarity, low_width, low_height, q_phase)
    if cache_key in _shimmer_cache:
        cached_surf = _shimmer_cache[cache_key]
        # Scale up to full size and return
        return pygame.transform.smoothscale(cached_surf, (width, height))

    # Get the precomputed normalized grid
    norm_grid = get_normalized_grid(low_width, low_height)

    # Compute the shifted grid based on phase (only need to do modulo on the precomputed grid)
    diag = (norm_grid + phase) % 1.0

    # Compute blend factor for shimmer effect
    blend = np.abs(diag - 0.5) * 2  
    shimmer_width = 0.3  
    blend = 1 - np.clip(blend / shimmer_width, 0, 1)
    blend = blend[:, :, None]  # Add a channel axis

    # Precompute base and bright colors (as float32 arrays)
    base_color = np.array(rarity_color, dtype=np.float32)
    bright_offset = 30 if rarity == "Exclusive" else 70
    bright_color = np.minimum(base_color + bright_offset, 255)

    # Compute the final pixel array
    pixel_array = base_color * (1 - blend) + bright_color * blend
    pixel_array = np.clip(pixel_array, 0, 255).astype(np.uint8)

    # Create or update the low-res surface
    if surface is None:
        surface = pygame.Surface((low_width, low_height))
    pygame.surfarray.blit_array(surface, np.transpose(pixel_array, (1, 0, 2)))

    # Cache the computed low-res surface
    _shimmer_cache[cache_key] = surface.copy()

    # Scale up to full size before returning
    return pygame.transform.smoothscale(surface, (width, height))

def generate_shades(base_color, variation=30):
    """Generate a random shade of the given base color with slight variation."""
    r, g, b = base_color
    return (
        max(0, min(255, r + random.randint(-variation, variation))),
        max(0, min(255, g + random.randint(-variation, variation))),
        max(0, min(255, b + random.randint(-variation, variation)))
    )

_cached_bg_image = None
def get_background_image():
    global _cached_bg_image
    if _cached_bg_image is None:
        bg = pygame.image.load("assets/ui/menu_bg.png").convert()
        _cached_bg_image = pygame.transform.scale(bg, (game_state.screen_width, game_state.screen_height))
    return _cached_bg_image
