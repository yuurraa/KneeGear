import pygame
import random

import src.engine.game_state as game_state
import src.engine.constants as constants
from src.engine.helpers import get_ui_scaling_factor
import src.engine.score as score
    
ui_scaling_factor = get_ui_scaling_factor()
    
def draw_experience_bar():
    screen = game_state.screen
    bar_width = game_state.screen_width
    bar_height = 30 * ui_scaling_factor
    bar_x = 0
    bar_y = game_state.screen_height - bar_height

    # Create a translucent surface for the background
    background_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    background_surf.fill((0, 0, 0, 128))  # Black with 50% opacity

    # Blit the translucent background onto the screen
    screen.blit(background_surf, (bar_x, bar_y))

    # Draw the border
    pygame.draw.rect(screen, constants.BLACK, (bar_x - 4 * ui_scaling_factor, bar_y - 4 * ui_scaling_factor, bar_width + 8 * ui_scaling_factor, bar_height + 8 * ui_scaling_factor), int(4 * ui_scaling_factor))

    # Calculate the filled width based on current experience
    filled_width = int((game_state.player.player_experience / game_state.player.experience_to_next_level) * bar_width)

    # Create a translucent blue surface for the filled portion
    filled_surf = pygame.Surface((filled_width, bar_height), pygame.SRCALPHA)
    filled_surf.fill((0, 0, 255, 128))  # Blue with 50% opacity

    # Blit the filled portion onto the screen
    screen.blit(filled_surf, (bar_x, bar_y))

    
def draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress, fps):
    screen = game_state.screen
    icon_size = 140 * ui_scaling_factor  # Size of each icon
    padding = 20 * ui_scaling_factor    # Space between icons
    x = game_state.screen_width - icon_size - padding  # Position at top-right corner
    y = padding + 120 * ui_scaling_factor

    # --- Draw FPS Counter ---
    fps_text = f"FPS: {fps:.0f}"
    
    # Render FPS text with a black border (outline effect)
    text_surface = game_state.FONTS["small"].render(fps_text, True, constants.WHITE)
    text_outline = game_state.FONTS["small"].render(fps_text, True, constants.BLACK)

    # FPS position (below the timer, aligned along the same X-axis)
    fps_x = x - 146 * ui_scaling_factor
    fps_y = y + icon_size + padding - 180 * ui_scaling_factor  # Adjust the value to fine-tune the placement

    # Draw black outline for better visibility (offset slightly in multiple directions)
    screen.blit(text_outline, (int(fps_x - 2 * ui_scaling_factor), int(fps_y - 2 * ui_scaling_factor)))
    screen.blit(text_outline, (int(fps_x + 2 * ui_scaling_factor), int(fps_y - 2 * ui_scaling_factor)))
    screen.blit(text_outline, (int(fps_x - 2 * ui_scaling_factor), int(fps_y + 2 * ui_scaling_factor)))
    screen.blit(text_outline, (int(fps_x + 2 * ui_scaling_factor), int(fps_y + 2 * ui_scaling_factor)))
    screen.blit(text_surface, (fps_x, fps_y))

    # --- Draw Left Click Icon ---
    left_icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    pygame.draw.rect(left_icon_surface, (255, 255, 255, 128), (0, 0, icon_size, icon_size))  # Translucent white background
    text = game_state.FONTS["medium"].render("L", True, (0, 0, 0))  # Black "L"
    text_rect = text.get_rect(center=(icon_size // 2, icon_size // 2))
    left_icon_surface.blit(text, text_rect)

    # Apply cooldown effect (draw overlay if not ready)
    if left_click_cooldown_progress < 1:
        cooldown_height = int((1 - left_click_cooldown_progress) * icon_size)
        pygame.draw.rect(left_icon_surface, (0, 0, 0, 128),
                         (0, icon_size - cooldown_height, icon_size, cooldown_height))
    pygame.draw.rect(left_icon_surface, constants.BLACK, (0, 0, icon_size, icon_size), 2)
    screen.blit(left_icon_surface, (x, y - 20 * ui_scaling_factor))

    # --- Draw Right Click Icon ---
    y += icon_size + padding  # Position below the left icon
    right_icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    pygame.draw.rect(right_icon_surface, (255, 255, 255, 128), (0, 0, icon_size, icon_size))
    text = game_state.FONTS["medium"].render("R", True, (0, 0, 0))  # Black "R"
    text_rect = text.get_rect(center=(icon_size // 2, icon_size // 2))
    right_icon_surface.blit(text, text_rect)
    if right_click_cooldown_progress < 1:
        cooldown_height = int((1 - right_click_cooldown_progress) * icon_size)
        pygame.draw.rect(right_icon_surface, (0, 0, 0, 128),
                         (0, icon_size - cooldown_height, icon_size, cooldown_height))
    pygame.draw.rect(right_icon_surface, constants.BLACK, (0, 0, icon_size, icon_size), 2)
    screen.blit(right_icon_surface, (x, y - 20 * ui_scaling_factor))

def draw_health_bar(x, y, health, max_health, color, bar_width=200, bar_height=10):
    screen = game_state.screen
    filled_width = int((health / max_health) * bar_width)
    surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, int(380 * ui_scaling_factor)), (0, 0, bar_width, bar_height))
    pygame.draw.rect(surface, color, (0, 0, filled_width, bar_height))
    pygame.draw.rect(surface, constants.BLACK, (0, 0, bar_width, bar_height), 1) 
    screen.blit(surface, (x, y))

def draw_fade_overlay():
    screen = game_state.screen
    fade_surface = pygame.Surface((game_state.screen_width, game_state.screen_height))
    fade_surface.set_alpha(game_state.fade_alpha)
    fade_surface.fill(constants.BLACK)
    screen.blit(fade_surface, (0, 0))

def draw_player_state_value_updates():
    if not game_state.running:  # Clear all updates if the game is not running
        game_state.damage_numbers.clear()
        game_state.experience_updates.clear()
        return
    
    screen = game_state.screen

    # Draw damage numbers
    for update in game_state.damage_numbers[:]:
        # Generate and store x_offset if it doesn't exist
        if "x_offset" not in update:
            update["x_offset"] = random.randint(-60, 60)
            
        display_value = int(update["value"])
        text = game_state.FONTS["tiny"].render(str(display_value), True, update["color"])
        text_surface = text.convert_alpha()
        screen.blit(text_surface, (update["x"] - text.get_width() // 2 + update["x_offset"], 
                                 update["y"] - text.get_height() // 2 + random.randint(-1, 1)))

        from src.player.player import PlayerState
        if not game_state.paused and not game_state.showing_stats and not game_state.showing_upgrades and game_state.player.state != PlayerState.LEVELING_UP:
            update["y"] -= 6 * ui_scaling_factor
            update["timer"] -= 1

            if update["timer"] <= 0:
                game_state.damage_numbers.remove(update)

    # Draw experience pop-ups
    for exp_update in game_state.experience_updates[:]:
        # Generate and store x_offset if it doesn't exist
        if "x_offset" not in exp_update:
            exp_update["x_offset"] = random.randint(-2, 2)
            
        text = game_state.FONTS["tiny"].render(f"+{exp_update['value']} EXP", True, exp_update["color"])
        text_surface = text.convert_alpha()
        screen.blit(text_surface, (exp_update["x"] - text.get_width() // 2 + exp_update["x_offset"], 
                                 exp_update["y"] - 30 * ui_scaling_factor - text.get_height() // 2))

        from src.player.player import PlayerState
        if not game_state.paused and not game_state.showing_stats and not game_state.showing_upgrades and game_state.player.state != PlayerState.LEVELING_UP:
            exp_update["y"] -= 2 * ui_scaling_factor  # Move up by 1 pixel per frame
            exp_update["timer"] -= 1

            if exp_update["timer"] <= 0:
                game_state.experience_updates.remove(exp_update)
            
def draw_notification():
    if not game_state.running:
        game_state.notification_visible = False
        game_state.notification_message = ""
        game_state.notification_queue = []
    
    # Check if a notification is currently active.
    if not game_state.notification_visible:
        # print("DEBUG: No active notification. Checking queue...")
        if hasattr(game_state, "notification_queue") and game_state.notification_queue:
            game_state.notification_message = game_state.notification_queue.pop(0)
            game_state.notification_visible = True
            game_state.notification_timer = game_state.notification_total_duration
            # print(f"DEBUG: New notification loaded: {game_state.notification_message}")
        else:
            # print("DEBUG: No notifications in queue. Exiting draw_notification.")
            return

    total_duration = game_state.notification_total_duration
    slide_in_duration = game_state.notification_slide_in_duration
    visible_duration = game_state.notification_visible_duration
    slide_out_duration = game_state.notification_slide_out_duration

    from src.player.player import PlayerState
    # Determine whether to freeze the notification (if paused or in upgrades/stats)
    freeze = game_state.paused or game_state.showing_upgrades or game_state.showing_stats or game_state.player.state == PlayerState.LEVELING_UP

    if freeze:
        if not hasattr(game_state, 'notification_frozen_elapsed'):
            game_state.notification_frozen_elapsed = total_duration - game_state.notification_timer
        elapsed = game_state.notification_frozen_elapsed
        # print(f"DEBUG: Notification frozen, elapsed={elapsed}")
    else:
        elapsed = total_duration - game_state.notification_timer
        # print(f"DEBUG: Notification active, elapsed={elapsed}, timer={game_state.notification_timer}")

    target_y = 60 * ui_scaling_factor  # Final y-coordinate when fully visible

    # Calculate the current y position
    if elapsed < slide_in_duration:
        progress = elapsed / slide_in_duration
        y = -120 * ui_scaling_factor + (target_y + 120 * ui_scaling_factor) * progress
        # print(f"DEBUG: Sliding in, y={y}")
    elif elapsed < slide_in_duration + visible_duration:
        y = target_y
        # print(f"DEBUG: Fully visible, y={y}")
    elif elapsed < slide_in_duration + visible_duration + slide_out_duration:
        progress = (elapsed - slide_in_duration - visible_duration) / slide_out_duration
        y = target_y - (target_y + 120 * ui_scaling_factor) * progress
        # print(f"DEBUG: Sliding out, y={y}")
    else:
        # print(f"DEBUG: Notification '{game_state.notification_message}' finished.")
        game_state.notification_visible = False
        game_state.notification_message = ''
        if hasattr(game_state, 'notification_frozen_elapsed'):
            del game_state.notification_frozen_elapsed

        # If there are more notifications, load the next one.
        if hasattr(game_state, "notification_queue") and game_state.notification_queue:
            game_state.notification_message = game_state.notification_queue.pop(0)
            game_state.notification_visible = True
            game_state.notification_timer = game_state.notification_total_duration
            # print(f"DEBUG: Loading next notification: {game_state.notification_message}")
        return

    # Decrement the timer only if not freezing.
    if not freeze:
        game_state.notification_timer -= 1
        # print(f"DEBUG: Timer decremented to {game_state.notification_timer}")

    # Render the notification text.
    text_surface = game_state.FONTS["medium"].render(game_state.notification_message, True, constants.WHITE)
    text_rect = text_surface.get_rect(center=(game_state.screen_width // 2, y + 60 * ui_scaling_factor))

    # Calculate background box dimensions.
    padding = 60 * ui_scaling_factor
    box_width = text_rect.width + padding
    box_height = text_rect.height + padding
    box_rect = pygame.Rect((game_state.screen_width - box_width) // 2, y, box_width, box_height)
    background_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    background_surface.fill((50, 50, 50, 190))

    # Draw the background and border.
    game_state.screen.blit(background_surface, box_rect.topleft)
    pygame.draw.rect(game_state.screen, constants.BLACK, box_rect, int(4 * ui_scaling_factor))
    game_state.screen.blit(text_surface, text_rect)

    # print(f"DEBUG: Notification drawn: {game_state.notification_message}")
    
def show_intro_screen(screen, screen_width, screen_height):
    # Create text surface using design resolution
    text = game_state.FONTS["huge"].render("GOONER INC.", True, constants.WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Fade-in text on the dummy surface
    for alpha in range(0, 256, 5):
        screen.fill(constants.BLACK)
        text.set_alpha(alpha)
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(10)
    
    # Display text for 2 seconds
    pygame.time.wait(2000)
    
    # Fade-out to black using an overlay
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)
    game_state.fade_alpha = 255   

def show_game_over_screen(screen, screen_width, screen_height, alpha):
    game_over_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    game_over_surface.fill((0, 0, 0, alpha))
    
    text_large = game_state.FONTS["huge"].render("YOU DIED", True, constants.WHITE)
    text_large_rect = text_large.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
    game_over_surface.blit(text_large, text_large_rect)
    
    final_time = getattr(game_state, 'final_time', 0)
    minutes = final_time // 60
    seconds = final_time % 60
    timer_text = game_state.FONTS["medium"].render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
    timer_text_rect = timer_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
    game_over_surface.blit(timer_text, timer_text_rect)
    
    # Use the captured final score instead of the live score
    final_score = getattr(game_state, 'final_score', score.score)
    score_text = game_state.FONTS["medium"].render(f"Score: {final_score}", True, constants.WHITE)
    score_text_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
    game_over_surface.blit(score_text, score_text_rect)
    
    high_score_text = game_state.FONTS["medium"].render(f"High Score: {score.high_score}", True, constants.WHITE)
    high_score_text_rect = high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
    game_over_surface.blit(high_score_text, high_score_text_rect)
    
    restart_text = game_state.FONTS["medium"].render("Press SPACE to restart", True, constants.WHITE)
    restart_text_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    game_over_surface.blit(restart_text, restart_text_rect)
    
    version_text = game_state.FONTS["small"].render("Gooner Game v0.1.3 - (WIP)", True, constants.WHITE)
    version_text_rect = version_text.get_rect(center=(screen_width // 2, screen_height - 20))
    game_over_surface.blit(version_text, version_text_rect)
    
    screen.blit(game_over_surface, (0, 0))
