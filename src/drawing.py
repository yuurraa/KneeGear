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

def draw_enemy(x, y, health, enemy_type):
    screen = game_state.screen
    if enemy_type == "tank":
        # Draw tank enemy
        pygame.draw.rect(screen, constants.BLACK, (x - 26, y - 26, 52, 52))  # Larger outline
        pygame.draw.rect(screen, (139, 69, 19), (x - 25, y - 25, 50, 50))    # Brown
        max_health = 400
        bar_width = 50
    else:
        # Draw regular enemy
        pygame.draw.rect(screen, constants.BLACK, (x - 21, y - 21, 42, 42))  # Regular outline
        pygame.draw.rect(screen, constants.RED, (x - 20, y - 20, 40, 40))
        max_health = 100
        bar_width = 40

    # Calculate health bar position to center it above the enemy
    health_bar_x = x - bar_width // 2  # Center the health bar horizontally
    health_bar_y = y - 35  # Position the health bar above the enemy

    # Draw health bar
    draw_health_bar(
        health_bar_x,
        health_bar_y,
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

def draw_health_updates():
    screen = game_state.screen
    font = pygame.font.SysFont(None, 24)  # Adjust font size as needed

    for update in game_state.damage_numbers[:]:
        # Determine color and prefix based on whether it's healing or damage
        display_value = update["value"]
        if update["color"] == constants.YELLOW or update["color"] == constants.RED:
            # It's damage, show negative number
            display_value = f"-{display_value}"
        else:
            # It's healing, show positive number and use green color
            display_value = f"+{display_value}"
            update["color"] = constants.GREEN

        # Render the value
        text = font.render(str(display_value), True, update["color"])

        # Create a surface with per-pixel alpha
        text_surface = text.convert_alpha()

        # Position the text
        screen.blit(text_surface, (update["x"] - text.get_width() // 2, update["y"] - text.get_height() // 2))

        # Update position to make the number float upwards
        update["y"] -= 1  # Move up by 1 pixel per frame

        # Decrement timer
        update["timer"] -= 1

        # Remove the update if timer has expired
        if update["timer"] <= 0:
            game_state.damage_numbers.remove(update)
