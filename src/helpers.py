import math
import pygame
import os

import src.game_state as game_state
import src.constants as constants

def calculate_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def reset_game():
    
    game_state.player.reset()

    game_state.enemies.clear()
    game_state.projectiles.clear()
    game_state.hearts.clear()
    game_state.damage_numbers.clear()
    
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
    scale_x = game_state.DESIGN_WIDTH / game_state.screen_width
    scale_y = game_state.DESIGN_HEIGHT / game_state.screen_height
    return (int(mouse_pos[0] * scale_x), int(mouse_pos[1] * scale_y))

def get_ui_scaling_factor():
    return game_state.DESIGN_WIDTH / game_state.screen_width

def get_text_scaling_factor(font_size):
    return round(font_size * (game_state.screen_width / game_state.DESIGN_WIDTH) * 1.4)

def fade_from_black(surface, wait_time=10, step=5):
    """
    Assumes that 'surface' already has the new scene drawn underneath.
    Gradually removes a black overlay (alpha decreases from 255 to 0)
    so that the new scene is revealed.
    """
    overlay = pygame.Surface((game_state.DESIGN_WIDTH, game_state.DESIGN_HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(255, -1, -step):
        overlay.set_alpha(alpha)
        temp_surface = surface.copy()
        temp_surface.blit(overlay, (0, 0))
        scaled = pygame.transform.smoothscale(temp_surface, (game_state.screen_width, game_state.screen_height))
        game_state.screen.blit(scaled, (0, 0))
        pygame.display.flip()
        pygame.time.wait(wait_time)
    # Final update: ensure overlay is completely removed.
    scaled = pygame.transform.smoothscale(surface, (game_state.screen_width, game_state.screen_height))
    game_state.screen.blit(scaled, (0, 0))
    pygame.display.flip()

        
def fade_to_black(surface, wait_time=10, step=5):
    """
    Assumes that 'surface' already has the current scene drawn.
    Gradually overlays a black surface (alpha increases from 0 to 255)
    to fade the scene out.
    """
    overlay = pygame.Surface((game_state.DESIGN_WIDTH, game_state.DESIGN_HEIGHT))
    overlay.fill((0, 0, 0))
    for alpha in range(0, 256, step):
        overlay.set_alpha(alpha)
        temp_surface = surface.copy()
        temp_surface.blit(overlay, (0, 0))
        scaled = pygame.transform.smoothscale(temp_surface, (game_state.screen_width, game_state.screen_height))
        game_state.screen.blit(scaled, (0, 0))
        pygame.display.flip()
        pygame.time.wait(wait_time)
    # Final update: ensure the screen is completely black.
    black_surface = pygame.Surface((game_state.DESIGN_WIDTH, game_state.DESIGN_HEIGHT))
    black_surface.fill((0, 0, 0))
    scaled = pygame.transform.smoothscale(black_surface, (game_state.screen_width, game_state.screen_height))
    game_state.screen.blit(scaled, (0, 0))
    pygame.display.flip()
