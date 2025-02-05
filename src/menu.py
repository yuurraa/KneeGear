import pygame
import constants
import game_state
from player import PlayerState
from upgrades import UpgradePool

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        color = (min(self.color[0] + 30, 255), 
                min(self.color[1] + 30, 255), 
                min(self.color[2] + 30, 255)) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, 2)  # Border

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, constants.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Slider:
    def __init__(self, x, y, width, height, value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value  # a float between 0 and 1
        # Define knob dimensions
        self.knob_width = 10
        self.knob_height = height + 4  # a little taller than the track
        # Colors (you can adjust these or pull them from constants)
        self.track_color = constants.LIGHT_GREY
        self.fill_color = constants.DARK_GREY  # Color for the filled portion
        self.knob_color = constants.WHITE
        self.dragging = False

    def draw(self, screen):
        # Define the track rectangle
        track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw the slider track (background) with a black border
        pygame.draw.rect(screen, self.track_color, track_rect)
        pygame.draw.rect(screen, constants.BLACK, track_rect, 2)  # 2-pixel black border

        # Calculate filled width based on current value
        filled_width = int(self.value * self.width)
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(screen, self.fill_color, filled_rect)
        
        # Calculate knob position (no border for the knob)
        knob_x = self.x + filled_width - self.knob_width // 2
        knob_y = self.y + (self.height - self.knob_height) // 2
        pygame.draw.rect(screen, self.knob_color, (knob_x, knob_y, self.knob_width, self.knob_height))
        pygame.draw.rect(screen, constants.BLACK, (knob_x, knob_y, self.knob_width, self.knob_height), 2)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Calculate knob's x position based on current value
            knob_x = self.x + (self.value * (self.width - self.knob_width))
            # Create knob rect using self.x, self.y, self.width, and self.height
            knob_rect = pygame.Rect(
                knob_x,
                self.y + self.height // 2 - self.knob_height // 2,
                self.knob_width,
                self.knob_height
            )
            # Also create a rect for the slider track
            track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if knob_rect.collidepoint(mouse_pos) or track_rect.collidepoint(mouse_pos):
                self.dragging = True
                # Update position if clicked on track
                mouse_x = mouse_pos[0]
                new_knob_x = max(
                    self.x,
                    min(mouse_x - self.knob_width / 2, self.x + self.width - self.knob_width)
                )
                self.value = (new_knob_x - self.x) / (self.width - self.knob_width)
                constants.music_volume = self.value
                pygame.mixer.music.set_volume(self.value)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            new_knob_x = max(
                self.x,
                min(mouse_x - self.knob_width / 2, self.x + self.width - self.knob_width)
            )
            self.value = (new_knob_x - self.x) / (self.width - self.knob_width)
            constants.music_volume = self.value
            pygame.mixer.music.set_volume(self.value)

class UpgradeButton(Button):
    RARITY_COLORS = {
        "Common": (144, 238, 144),  # Light green
        "Rare": (135, 206, 250),    # Light blue
        "Epic": (186, 85, 211),     # Light purple
        "Mythic": (255, 71, 76),      # Red
        "Legendary": (255, 215, 0),    # Gold
    }

    def __init__(self, x, y, width, height, upgrade, icon_image=None):
        rarity_color = self.RARITY_COLORS.get(upgrade.Rarity, constants.GREEN)
        super().__init__(x, y, width, height, "", rarity_color)
        self.upgrade = upgrade
        self.icon_image = icon_image  # Store the icon image
        self.width = width  # Explicitly set width
        self.height = height  # Explicitly set height
        self.icon_size = 64  # Fixed icon size
        self.circle_margin = 10  # Margin around the circle


    def draw(self, screen):
        super().draw(screen)

        font_name = pygame.font.Font(None, 32)
        font_desc = pygame.font.Font(None, 24)
        font_rarity = pygame.font.Font(None, 20)

        # Draw the icon in a circle overlapping the top-left corner
        if self.icon_image:
            # Fixed icon size
            icon_scaled = pygame.transform.scale(self.icon_image, (self.icon_size - 34, self.icon_size - 34))

            # Calculate circle properties
            circle_radius = self.icon_size // 2 - 5
            circle_center = (self.rect.x + circle_radius - self.circle_margin - 15, 
                             self.rect.y + circle_radius - self.circle_margin - 15)

            # Draw circular background with button color and border
            pygame.draw.circle(screen, self.color, circle_center, circle_radius)  # Match button background
            pygame.draw.circle(screen, constants.BLACK, circle_center, circle_radius, 2)  # Black border

            # Blit the icon image centered in the circle
            icon_rect = icon_scaled.get_rect(center=circle_center)
            screen.blit(icon_scaled, icon_rect)

        # Centralized title text (with wrapping)
        words = self.upgrade.name.split()
        title_lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font_name.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - 20:  # 20px padding on each side
                current_line.append(word)
            else:
                if current_line:
                    title_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            title_lines.append(' '.join(current_line))

        # Render wrapped title text
        title_y = self.rect.y + 20 + (self.icon_size - 47)  # Space below the circle
        for line in title_lines:
            title_surface = font_name.render(line, True, constants.BLACK)
            title_rect = title_surface.get_rect(center=(self.rect.centerx, title_y))
            screen.blit(title_surface, title_rect)
            title_y += title_surface.get_height()

        # Render rarity below the title
        rarity_surface = font_rarity.render(self.upgrade.Rarity, True, constants.BLACK)
        rarity_rect = rarity_surface.get_rect(center=(self.rect.centerx, title_y - 2))
        screen.blit(rarity_surface, rarity_rect)

        # Centralized description text (with wrapping)
        desc_words = self.upgrade.description.split()
        desc_lines = []
        current_desc_line = []

        for word in desc_words:
            test_line = ' '.join(current_desc_line + [word])
            test_surface = font_desc.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - 20:  # 20px padding on each side
                current_desc_line.append(word)
            else:
                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))
                current_desc_line = [word]
        if current_desc_line:
            desc_lines.append(' '.join(current_desc_line))

        # Render wrapped description text below rarity
        y_offset = rarity_rect.bottom + 18
        for line in desc_lines:
            desc_surface = font_desc.render(line, True, constants.BLACK)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(desc_surface, desc_rect)
            y_offset += desc_surface.get_height()


def draw_level_up_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create menu panel - using proportional sizes
    panel_width = int(game_state.screen_width * 0.65)  # ~57% of screen width
    panel_height = int(game_state.screen_height * 0.37)  # ~37% of screen height
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Level up text
    font = pygame.font.Font(None, 48)
    text = font.render(f"Level {game_state.player.player_level} - Choose an Upgrade", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + 50))
    screen.blit(text, text_rect)

    # Create buttons if they don't exist
    if not hasattr(game_state, 'current_upgrade_buttons'):
        # Get random upgrades
        upgrade_pool = UpgradePool()
        upgrades = upgrade_pool.get_random_upgrades(3, game_state.player)
        
        # Create buttons with proportional sizes
        button_width = int(game_state.screen_width * 0.18)  # ~16% of screen width
        button_height = int(game_state.screen_height * 0.18)  # ~15% of screen height
        button_spacing = int(game_state.screen_width * 0.026)  # ~2.6% of screen width
        total_width = (button_width * 3) + (button_spacing * 2)
        start_x = (game_state.screen_width - total_width) // 2

        game_state.current_upgrade_buttons = []
        for i, upgrade in enumerate(upgrades):
            x = start_x + (button_width + button_spacing) * i
            y = panel_y + 150
            icon_image = upgrade_pool.icon_images.get(upgrade.icon, None)
            button = UpgradeButton(x, y, button_width, button_height, upgrade, icon_image)
            game_state.current_upgrade_buttons.append(button)

    # Draw existing buttons
    for button in game_state.current_upgrade_buttons:
        button.draw(screen)

    return game_state.current_upgrade_buttons

def draw_pause_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create menu panel with proportional sizes
    panel_width = int(game_state.screen_width * 0.28)  # ~26% of screen width
    panel_height = int(game_state.screen_height * 0.35)  # ~32% of screen height
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Pause menu text
    font = pygame.font.Font(None, 48)
    text = font.render("Paused", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + 50))
    screen.blit(text, text_rect)

    # Initialize UI elements once
    if not hasattr(game_state, 'pause_ui'):
        # Button dimensions - proportional
        button_width = int(game_state.screen_width * 0.104)  # ~10.4% of screen width
        button_height = int(game_state.screen_height * 0.056)  # ~5.6% of screen height

        # Calculate positions for buttons
        button_x = (game_state.screen_width - (button_width * 2 + int(game_state.screen_width * 0.01))) // 2
        button_y = panel_y + int(panel_height * 0.74)  # ~74% down the panel

        # Quit button
        quit_button = Button(button_x + button_width + 20, button_y, button_width, button_height, "Quit", constants.RED)

        # Resume button
        resume_button = Button(button_x, button_y, button_width, button_height, "Resume", constants.GREEN)

        # Volume Slider - proportional
        slider_width = int(game_state.screen_width * 0.156)  # ~15.6% of screen width
        slider_height = int(game_state.screen_height * 0.019)  # ~1.9% of screen height
        slider_x = (game_state.screen_width - slider_width) // 2
        slider_y = panel_y + int(panel_height * 0.34)  # ~34% down the panel
        volume_slider = Slider(slider_x, slider_y, slider_width, slider_height, constants.music_volume)

        # Centralize Upgrades Button
        upgrades_button_x = (game_state.screen_width - button_width) // 2
        upgrades_button = Button(upgrades_button_x, slider_y + 50, button_width, button_height, "Upgrades", constants.BLUE)

        game_state.pause_ui = {
            'quit_button': quit_button,
            'resume_button': resume_button,
            'volume_slider': volume_slider,
            'upgrades_button': upgrades_button
        }

    # Draw persistent elements
    game_state.pause_ui['quit_button'].draw(screen)
    game_state.pause_ui['resume_button'].draw(screen)
    game_state.pause_ui['volume_slider'].draw(screen)
    game_state.pause_ui['upgrades_button'].draw(screen)

    # Draw "Volume" label above the slider
    small_font = pygame.font.Font(None, 30)
    volume_text = small_font.render("Volume", True, constants.BLACK)
    volume_text_rect = volume_text.get_rect(center=(game_state.screen_width // 2, panel_y + 100))
    screen.blit(volume_text, volume_text_rect)

    return game_state.pause_ui['quit_button'], game_state.pause_ui['resume_button'], game_state.pause_ui['volume_slider'], game_state.pause_ui['upgrades_button']

def draw_upgrades_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Constants for button dimensions - now based on screen proportions
    button_width = int(game_state.screen_width * 0.24)  # ~19% of screen width
    button_height = int(game_state.screen_height * 0.046)  # ~4.6% of screen height
    button_spacing = int(game_state.screen_height * 0.019)  # ~1.9% of screen height
    max_column_height = int(game_state.screen_height * 0.7)  # 70% of screen height
    title_height = int(game_state.screen_height * 0.037)  # ~3.7% of screen height
    close_button_height = int(game_state.screen_height * 0.046)  # ~4.6% of screen height

    # Calculate the number of upgrades
    num_upgrades = len(game_state.player.applied_upgrades)

    # Calculate panel dimensions
    base_panel_width = int(game_state.screen_width * 0.3)  # ~570px on 1920px width
    panel_height = int(game_state.screen_height * 0.185) + min(
        (button_height * num_upgrades) + (button_spacing * (num_upgrades - 1)), 
        max_column_height
    )  # 200px base + dynamic height

    # Calculate the number of columns needed
    num_columns = (int(game_state.screen_height * 0.046) + (button_height * num_upgrades) + 
                  (button_spacing * (num_upgrades - 1))) // max_column_height + 1

    # Calculate panel width based on number of columns
    column_width = int(game_state.screen_width * 0.193)  # ~370px on 1920px width
    panel_width = base_panel_width + (num_columns - 1) * column_width

    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw title text
    title_font = pygame.font.Font(None, 36)  # Reduced font size for title
    desc_font = pygame.font.Font(None, 28)    # Reduced font size for description

    title_surface = title_font.render("Obtained Upgrades", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + title_height // 2 + 10))  # Moved down by 10px
    screen.blit(title_surface, title_rect)

    # Display upgrades
    y_offset = panel_y + title_height + 30  # Updated starting y position
    column_index = 0  # Track the current column

    for i, upgrade in enumerate(game_state.player.applied_upgrades):
        # Determine the rarity color
        rarity_color = UpgradeButton.RARITY_COLORS.get(upgrade.Rarity, constants.LIGHT_GREY)

        # Calculate the x position for the current column
        x_offset = panel_x + (panel_width / num_columns) * column_index + (panel_width / num_columns - button_width) / 2

        # Append the count of the upgrade to its name
        upgrade_count = game_state.player.upgrade_levels.get(upgrade.name, 0)
        display_name = f"{upgrade.name} ({upgrade_count}x)"  # Append count

        # Create a button for each upgrade with the rarity color, but set the text to an empty string
        button = Button(x_offset, y_offset, button_width, button_height, "", rarity_color)
        button.draw(screen)  # Draw the button

        # Use desc_font to render the upgrade name inside the button
        name_surface = desc_font.render(display_name, True, constants.BLACK)
        name_rect = name_surface.get_rect(center=(x_offset + button_width // 2, y_offset + button_height // 2))
        screen.blit(name_surface, name_rect)

        # Update y_offset for the next button
        y_offset += button_height + button_spacing

        # Check if we need to move to the next column
        if y_offset + button_height > panel_y + title_height + 30 + max_column_height:
            y_offset = panel_y + title_height + 30  # Reset y_offset for the new column
            column_index += 1  # Move to the next column

    # Add a close button with a dead zone
    close_button_x = panel_x + (panel_width - 100) // 2  # Centralize the close button
    close_button = Button(close_button_x, panel_y + panel_height - close_button_height - 20, 90, close_button_height, "Close", constants.RED)
    close_button.draw(screen)
    return close_button

