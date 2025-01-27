import pygame
import math
import game_state
import constants
from helpers import calculate_angle


def draw_player(x, y, angle):
    screen = game_state.screen
    pygame.draw.rect(screen, constants.BLACK, (x - 16, y - 16, 22, 22))  # Outline
    pygame.draw.rect(screen, constants.GREEN, (x - 15, y - 15, 20, 20))
    arrow_length = 20
    arrow_x = x + arrow_length * math.cos(math.radians(angle))
    arrow_y = y + arrow_length * math.sin(math.radians(angle))
    pygame.draw.line(screen, constants.BLUE, (x, y), (arrow_x, arrow_y), 3)

def draw_health_bar(x, y, health, max_health, color, bar_width=100, bar_height=10):
    screen = game_state.screen
    filled_width = int((health / max_health) * bar_width)
    surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    pygame.draw.rect(surface, constants.BLACK, (0, 0, bar_width, bar_height))
    pygame.draw.rect(surface, color, (0, 0, filled_width, bar_height))
    screen.blit(surface, (x, y))

def draw_enemy(x, y, health, enemy_type):
    screen = game_state.screen
    if enemy_type == "tank":
        pygame.draw.rect(screen, constants.BLACK, (x - 26, y - 26, 52, 52))  # Larger outline
        pygame.draw.rect(screen, (139, 69, 19), (x - 25, y - 25, 50, 50))    # Brown
        max_health = 400
        bar_width = 50
    else:
        pygame.draw.rect(screen, constants.BLACK, (x - 21, y - 21, 42, 42))  # Regular outline
        pygame.draw.rect(screen, constants.RED, (x - 20, y - 20, 40, 40))
        max_health = 100
        bar_width = 40

    draw_health_bar(
        x - 25,
        y - 35,
        health,
        max_health,
        constants.TRANSLUCENT_RED,
        bar_width=bar_width,
        bar_height=5
    )

def draw_fade_overlay():
    screen = game_state.screen
    fade_surface = pygame.Surface((game_state.screen_width, game_state.screen_height))
    fade_surface.set_alpha(game_state.fade_alpha)
    fade_surface.fill(constants.BLACK)
    screen.blit(fade_surface, (0, 0))

def draw_projectiles():
    screen = game_state.screen
    for bullet in game_state.projectiles:
        # Special bullet
        if len(bullet) > 3 and bullet[3] == "special":
            pygame.draw.circle(screen, (255, 165, 0), (int(bullet[0]), int(bullet[1])), constants.player_special_bullet_size)
        else:
            pygame.draw.circle(screen, constants.BLUE, (int(bullet[0]), int(bullet[1])), constants.player_bullet_size)

def draw_damage_numbers():
    screen = game_state.screen
    font = pygame.font.SysFont(None, 24)  # Adjust font size as needed

    for dmg in game_state.damage_numbers[:]:
        # Render the damage value
        text = font.render(str(dmg["value"]), True, dmg["color"])

        # Create a surface with per-pixel alpha
        text_surface = text.convert_alpha()

        # Position the text
        screen.blit(text_surface, (dmg["x"] - text.get_width() // 2, dmg["y"] - text.get_height() // 2))

        # Update position to make the number float upwards
        dmg["y"] -= 1  # Move up by 1 pixel per frame

        # Decrement timer
        dmg["timer"] -= 1

        # Remove the damage number if timer has expired
        if dmg["timer"] <= 0:
            game_state.damage_numbers.remove(dmg)