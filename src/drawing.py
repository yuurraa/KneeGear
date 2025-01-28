import pygame
import math
import game_state
import constants
import random
from helpers import calculate_angle
    
def draw_experience_bar():
    screen = game_state.screen
    bar_width = game_state.screen_width
    bar_height = 10
    bar_x = 0
    bar_y = game_state.screen_height - bar_height

    # Draw the background of the experience bar
    pygame.draw.rect(screen, constants.BLACK, (bar_x, bar_y, bar_width, bar_height))

    # Calculate the filled width based on current experience
    filled_width = int((game_state.player.player_experience / game_state.player.experience_to_next_level) * bar_width)
    pygame.draw.rect(screen, (0, 0, 255, 128), (bar_x, bar_y, filled_width, bar_height))  # Translucent blue
    
def draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress):
    screen = game_state.screen
    icon_size = 50  # Size of each icon
    padding = 10  # Space between icons
    x = game_state.screen_width - icon_size - padding  # Position at top-right corner
    y = padding + 60

    # Draw left click icon
    left_icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    pygame.draw.rect(left_icon_surface, (255, 255, 255, 128), (0, 0, icon_size, icon_size))  # Translucent white
    font = pygame.font.Font(None, 36)
    text = font.render("L", True, (0, 0, 0))  # Black "L"
    text_rect = text.get_rect(center=(icon_size // 2, icon_size // 2))
    left_icon_surface.blit(text, text_rect)

    # Apply cooldown effect
    if left_click_cooldown_progress < 1:
        cooldown_height = int((1 - left_click_cooldown_progress) * icon_size)
        pygame.draw.rect(left_icon_surface, (0, 0, 0, 128), (0, icon_size - cooldown_height, icon_size, cooldown_height))  # Grey overlay

    screen.blit(left_icon_surface, (x, y))

    # Draw right click icon
    y += icon_size + padding  # Position below the left icon
    right_icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    pygame.draw.rect(right_icon_surface, (255, 255, 255, 128), (0, 0, icon_size, icon_size))  # Translucent white
    text = font.render("R", True, (0, 0, 0))  # Black "R"
    text_rect = text.get_rect(center=(icon_size // 2, icon_size // 2))
    right_icon_surface.blit(text, text_rect)

    # Apply cooldown effect
    if right_click_cooldown_progress < 1:
        cooldown_height = int((1 - right_click_cooldown_progress) * icon_size)
        pygame.draw.rect(right_icon_surface, (0, 0, 0, 128), (0, icon_size - cooldown_height, icon_size, cooldown_height))  # Grey overlay

    screen.blit(right_icon_surface, (x, y))

def draw_health_bar(x, y, health, max_health, color, bar_width=100, bar_height=10):
    screen = game_state.screen
    filled_width = int((health / max_health) * bar_width)
    surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    pygame.draw.rect(surface, constants.BLACK, (0, 0, bar_width, bar_height))
    pygame.draw.rect(surface, color, (0, 0, filled_width, bar_height))
    screen.blit(surface, (x, y))

def draw_enemy(enemy):
    screen = game_state.screen
    if enemy.type == "tank":
        # Draw tank enemy
        pygame.draw.rect(screen, constants.BLACK, (enemy.x - 26, enemy.y - 26, 52, 52))
        pygame.draw.rect(screen, (139, 69, 19), (enemy.x - 25, enemy.y - 25, 50, 50))
        bar_width = 50
    else:
        # Draw regular enemy
        pygame.draw.rect(screen, constants.BLACK, (enemy.x - 21, enemy.y - 21, 42, 42))
        pygame.draw.rect(screen, constants.RED, (enemy.x - 20, enemy.y - 20, 40, 40))
        bar_width = 40

    # Calculate health bar position
    health_bar_x = enemy.x - bar_width // 2
    health_bar_y = enemy.y - 35

    # Draw health bar
    draw_health_bar(
        health_bar_x,
        health_bar_y,
        enemy.health,
        enemy.max_health,
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

def draw_player_state_value_updates():
    screen = game_state.screen
    font = pygame.font.SysFont(None, 24)  # Adjust font size as needed

    # Draw damage numbers
    for update in game_state.damage_numbers[:]:
        # Generate and store x_offset if it doesn't exist
        if "x_offset" not in update:
            update["x_offset"] = random.randint(-60, 60)
            
        display_value = update["value"]
        text = font.render(str(display_value), True, update["color"])
        text_surface = text.convert_alpha()
        screen.blit(text_surface, (update["x"] - text.get_width() // 2 + update["x_offset"], 
                                 update["y"] - text.get_height() // 2 + random.randint(-1, 1)))

        update["y"] -= 3
        update["timer"] -= 1

        if update["timer"] <= 0:
            game_state.damage_numbers.remove(update)

    # Draw experience pop-ups
    for exp_update in game_state.experience_updates[:]:
        # Generate and store x_offset if it doesn't exist
        if "x_offset" not in exp_update:
            exp_update["x_offset"] = random.randint(-2, 2)
            
        text = font.render(f"+{exp_update['value']} EXP", True, exp_update["color"])
        text_surface = text.convert_alpha()
        screen.blit(text_surface, (exp_update["x"] - text.get_width() // 2 + exp_update["x_offset"], 
                                 exp_update["y"] - 15 - text.get_height() // 2))

        exp_update["y"] -= 1  # Move up by 1 pixel per frame
        exp_update["timer"] -= 1

        if exp_update["timer"] <= 0:
            game_state.experience_updates.remove(exp_update)
            
