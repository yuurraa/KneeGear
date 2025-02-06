import pygame
import math
import random

from src.helpers import calculate_angle, get_scaled_font
import src.game_state as game_state
import src.constants as constants
import src.main as main

def draw_experience_bar():
    screen = game_state.screen
    # Use base (unscaled) values then apply scale only once at draw time.
    base_bar_width = game_state.screen_width
    base_bar_height = 10
    base_bar_x = 0
    # Position the bar at the bottom of the screen (in base coordinates)
    base_bar_y = game_state.screen_height - base_bar_height

    # Multiply once by scale for final dimensions/positions.
    bar_width = base_bar_width * game_state.scale
    bar_height = base_bar_height * game_state.scale
    bar_x = base_bar_x * game_state.scale
    bar_y = base_bar_y * game_state.scale

    # Draw the background of the experience bar
    pygame.draw.rect(screen, constants.BLACK, (bar_x, bar_y, bar_width, bar_height))

    # Calculate the filled width based on current experience (using base bar_width)
    filled_width = int((game_state.player.player_experience / game_state.player.experience_to_next_level) * bar_width)
    pygame.draw.rect(screen, (0, 0, 255, 128), (bar_x, bar_y, filled_width, bar_height))  # Translucent blue

def draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress):
    screen = game_state.screen
    base_icon_size = 50  # Base size of each icon
    base_padding = 10    # Base space between icons

    # Calculate base positions first
    base_x = game_state.screen_width - base_icon_size - base_padding  # Top-right (base)
    base_y = base_padding + 60

    # Scale the positions
    x = base_x * game_state.scale
    y = base_y * game_state.scale

    # --- LEFT CLICK ICON ---
    # Create a surface with scaled dimensions
    left_icon_size = base_icon_size * game_state.scale
    left_icon_surface = pygame.Surface((left_icon_size, left_icon_size), pygame.SRCALPHA)
    # Draw a translucent white rectangle. Note: Multiply each color channel as needed.
    pygame.draw.rect(
        left_icon_surface,
        (255, 255, 255, 128), 
        (0, 0, left_icon_size, left_icon_size)
    )
    font = pygame.font.Font(None, get_scaled_font(36))
    text = font.render("L", True, (0, 0, 0))  # Black "L"
    text_rect = text.get_rect(center=(left_icon_size // 2, left_icon_size // 2))
    left_icon_surface.blit(text, text_rect)

    # Apply cooldown effect
    if left_click_cooldown_progress < 1:
        # Calculate cooldown height in base units then scale
        base_cooldown_height = int((1 - left_click_cooldown_progress) * base_icon_size)
        cooldown_height = base_cooldown_height * game_state.scale
        pygame.draw.rect(
            left_icon_surface,
            (0, 0, 0, 128),
            (0, left_icon_size - cooldown_height, left_icon_size, cooldown_height)
        )

    screen.blit(left_icon_surface, (x, y))

    # --- RIGHT CLICK ICON ---
    # Update base_y for the right icon (adding icon size and padding)
    base_y += base_icon_size + base_padding
    y = base_y * game_state.scale  # Recalculate y

    # Create right icon surface with scaled dimensions
    right_icon_size = base_icon_size * game_state.scale
    right_icon_surface = pygame.Surface((right_icon_size, right_icon_size), pygame.SRCALPHA)
    pygame.draw.rect(
        right_icon_surface,
        (255, 255, 255, 128),
        (0, 0, right_icon_size, right_icon_size)
    )
    text = font.render("R", True, (0, 0, 0))  # Black "R"
    text_rect = text.get_rect(center=(right_icon_size // 2, right_icon_size // 2))
    right_icon_surface.blit(text, text_rect)

    # Apply cooldown effect
    if right_click_cooldown_progress < 1:
        base_cooldown_height = int((1 - right_click_cooldown_progress) * base_icon_size)
        cooldown_height = base_cooldown_height * game_state.scale
        pygame.draw.rect(
            right_icon_surface,
            (0, 0, 0, 128),
            (0, right_icon_size - cooldown_height, right_icon_size, cooldown_height)
        )

    screen.blit(right_icon_surface, (x, y))

def draw_health_bar(x, y, health, max_health, color, bar_width=100, bar_height=10):
    screen = game_state.screen
    # Compute filled width in base coordinates then scale.
    filled_width = int((health / max_health) * bar_width) * game_state.scale
    # Create surface using base dimensions scaled once
    surface = pygame.Surface((bar_width * game_state.scale, bar_height * game_state.scale), pygame.SRCALPHA)
    pygame.draw.rect(surface, constants.BLACK, (0, 0, bar_width * game_state.scale, bar_height * game_state.scale))
    pygame.draw.rect(surface, color, (0, 0, filled_width, bar_height * game_state.scale))
    # Assume x and y are provided in base coordinates; scale them once on blit.
    screen.blit(surface, (x * game_state.scale, y * game_state.scale))

def draw_fade_overlay():
    screen = game_state.screen
    fade_surface = pygame.Surface(
        (game_state.screen_width * game_state.scale, game_state.screen_height * game_state.scale)
    )
    fade_surface.set_alpha(game_state.fade_alpha)
    fade_surface.fill(constants.BLACK)
    screen.blit(fade_surface, (0, 0))

def draw_player_state_value_updates():
    screen = game_state.screen
    font = pygame.font.SysFont(None, get_scaled_font(24))  # Adjust font size as needed

    # Draw damage numbers
    for update in game_state.damage_numbers[:]:
        # Generate and store x_offset if it doesn't exist
        if "x_offset" not in update:
            update["x_offset"] = random.randint(-60, 60)
            
        display_value = int(update["value"])
        text = font.render(str(display_value), True, update["color"])
        text_surface = text.convert_alpha()
        # Scale x and y coordinates (and x_offset) exactly once
        scaled_x = update["x"] * game_state.scale + update["x_offset"] * game_state.scale
        scaled_y = update["y"] * game_state.scale + int(random.randint(-1, 1) * game_state.scale)
        screen.blit(
            text_surface,
            (scaled_x - text.get_width() // 2, scaled_y - text.get_height() // 2)
        )

        update["y"] -= 3  # These values remain in base space
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
        scaled_x = exp_update["x"] * game_state.scale + exp_update["x_offset"] * game_state.scale
        scaled_y = (exp_update["y"] - 15) * game_state.scale
        screen.blit(
            text_surface,
            (scaled_x - text.get_width() // 2, scaled_y - text.get_height() // 2)
        )

        exp_update["y"] -= 1  # In base space
        exp_update["timer"] -= 1

        if exp_update["timer"] <= 0:
            game_state.experience_updates.remove(exp_update)
            
def draw_notification():
    if game_state.notification_visible:
        # Define constants in base (unscaled) coordinates
        total_duration = game_state.notification_total_duration
        slide_in_duration = game_state.notification_slide_in_duration
        visible_duration = game_state.notification_visible_duration
        slide_out_duration = game_state.notification_slide_out_duration

        timer = game_state.notification_timer
        elapsed = total_duration - timer  # Frames elapsed since notification was triggered

        # Define target Y position (base value) where the notification should slide to
        target_y = 50  # base coordinate

        # Determine the current phase of the animation using base values
        if elapsed < slide_in_duration:
            # Sliding In: starts off-screen at y = -60 (base)
            progress = elapsed / slide_in_duration
            y_base = -60 + (target_y + 60) * progress
        elif elapsed < (slide_in_duration + visible_duration):
            # Fully Visible
            y_base = target_y
        elif elapsed < (slide_in_duration + visible_duration + slide_out_duration):
            # Sliding Out
            progress = (elapsed - slide_in_duration - visible_duration) / slide_out_duration
            y_base = target_y - (target_y + 60) * progress
        else:
            # Animation Complete
            game_state.notification_visible = False
            y_base = -60  # Reset position

        # Now scale the base y coordinate
        y = y_base * game_state.scale
        game_state.notification_current_y = y

        # Render the notification text
        font = pygame.font.SysFont(None, get_scaled_font(32.0))
        # Center the text horizontally at (screen_width//2) in base coords, then scale.
        text_surface = font.render(game_state.notification_message, True, constants.WHITE)
        text_rect = text_surface.get_rect(
            center=((game_state.screen_width // 2) * game_state.scale, (y + 21 * game_state.scale))
        )

        # Define box dimensions in base coordinates then scale once.
        base_padding = 20
        box_width = (text_rect.width + base_padding)
        box_height = (text_rect.height + base_padding)
        # Compute box_rect in base coordinates
        base_box_x = (game_state.screen_width - box_width) // 2
        base_box_y = y_base  # in base coords
        # Now scale the box_rect
        box_rect = pygame.Rect(
            base_box_x * game_state.scale,
            base_box_y * game_state.scale,
            box_width * game_state.scale,
            box_height * game_state.scale
        )

        # Draw the background box
        pygame.draw.rect(
            game_state.screen,
            (50, 50, 50, 255),  # Dark grey box (alpha is not scaled)
            box_rect
        )
        pygame.draw.rect(game_state.screen, constants.WHITE, box_rect, int(2 * game_state.scale))  # White border

        # Draw the text
        game_state.screen.blit(text_surface, text_rect)

        # Decrement the timer
        game_state.notification_timer -= 1
        if game_state.notification_timer <= 0:
            game_state.notification_visible = False
            game_state.notification_message = ''
