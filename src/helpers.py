import math
import pygame
import game_state


def calculate_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def reset_game():
    game_state.player_health = 100

    game_state.enemies.clear()
    game_state.projectiles.clear()
    game_state.enemy_bullets.clear()
    game_state.enemy_aoe_bullets.clear()
    game_state.hearts.clear()
    game_state.tank_pellets.clear()

    game_state.fade_alpha = 0
    game_state.game_over = False
