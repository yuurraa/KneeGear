import pygame

import src.engine.constants as constants
import src.engine.game_state as game_state
from src.engine.helpers import get_ui_scaling_factor
from src.ui.components.ui_buttons import Button, SkinButton

ui_scaling_factor = get_ui_scaling_factor()

def draw_main_menu(screen):
    # Create a semi-transparent overlay for the menu
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.WHITE)
    overlay.set_alpha(255)
    screen.blit(overlay, (0, 0))

    # Draw menu title
    title_text = game_state.FONTS["massive"].render("Gooner Game", True, constants.BLACK)
    title_rect = title_text.get_rect(center=(game_state.screen_width // 2, game_state.screen_height // 2 - 100))
    screen.blit(title_text, title_rect)

    # Draw Start Game button
    start_button = Button(game_state.screen_width // 2 - 200 * ui_scaling_factor, game_state.screen_height // 2, 400 * ui_scaling_factor, 100 * ui_scaling_factor, "Start Game", constants.GREEN)
    start_button.draw(screen)

    # Draw Skin Selection button
    skin_button = Button(game_state.screen_width // 2 - 200 * ui_scaling_factor, game_state.screen_height // 2 + 120 * ui_scaling_factor, 400 * ui_scaling_factor, 100 * ui_scaling_factor, "Select Skin", constants.BLUE)
    skin_button.draw(screen)

    # Draw Quit button
    quit_button = Button(game_state.screen_width // 2 - 200 * ui_scaling_factor, game_state.screen_height // 2 + 240 * ui_scaling_factor, 400 * ui_scaling_factor, 100 * ui_scaling_factor, "Quit", constants.RED)
    quit_button.draw(screen)
    
    version_text = game_state.FONTS["small"].render("v0.1.3 - (WIP)", True, constants.BLACK)
    version_rect = version_text.get_rect(bottomright=(game_state.screen_width - 20 * ui_scaling_factor, game_state.screen_height - 20 * ui_scaling_factor))
    screen.blit(version_text, version_rect)

    return (start_button, quit_button, skin_button)

def draw_skin_selection_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.WHITE)
    overlay.set_alpha(255)
    screen.blit(overlay, (0, 0))

    # Draw title
    title_surface = game_state.FONTS["huge"].render("Select Your Skin", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(game_state.screen_width // 2, 100 * ui_scaling_factor))
    screen.blit(title_surface, title_rect)

    # Button dimensions
    button_width = int(game_state.screen_width * 0.15)
    button_height = int(game_state.screen_height * 0.075)
    button_spacing = 40 * ui_scaling_factor

    # Draw available skins as buttons with shimmer effect.
    # NOTE: If game_state.player.skins is now a dictionary, iterate over its values.
    skin_buttons = []
    for skin in game_state.player.skins.values():
        button_x = (game_state.screen_width - button_width) // 2
        button_y = 200 * ui_scaling_factor + (button_height + button_spacing) * len(skin_buttons)
      
        # Then draw the black border
        pygame.draw.rect(screen, constants.BLACK, (button_x, button_y, button_width, button_height), int(int(4 * ui_scaling_factor)))
        
        # Create a SkinButton and assign its skin_id
        skin_button = SkinButton(button_x, button_y, button_width, button_height, skin.name, skin.rarity)
        skin_button.skin_id = skin.id  # Set the unique skin ID
        skin_buttons.append(skin_button)

    # Reset glow timers before selecting a new button
    for button in skin_buttons:
        button.glow_timer = 0

    # Find the currently selected skin by ID (which is now stored in game_state.player.current_skin_id)
    current_skin_id = game_state.player.current_skin_id
    selected_button = next((btn for btn in skin_buttons if btn.skin_id == current_skin_id), None)

    if selected_button:
        selected_button.trigger_glow()

    # Draw close button (without shimmer)
    close_button_width = int(button_width * 0.6)
    close_button_height = int(button_height * 0.6)
    close_button_x = (game_state.screen_width - close_button_width) // 2
    close_button_y = game_state.screen_height - close_button_height - 60 * ui_scaling_factor
    close_button = Button(close_button_x, close_button_y, close_button_width, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (skin_buttons, close_button)