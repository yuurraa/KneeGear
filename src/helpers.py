import math
import pygame
import game_state


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
    game_state.last_enemy_spawn_time = pygame.time.get_ticks()  # Reset enemy spawn timer
    game_state.first_enemy_spawned = False  # Reset first enemy spawn flag
    
