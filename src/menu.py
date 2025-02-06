import pygame
import numpy as np
from src.helpers import save_music_settings, get_scaled_font
import src.constants as constants
import src.game_state as game_state
from src.player import PlayerState
from src.upgrades import UpgradePool
import math

class Button:
    def __init__(self, x, y, width, height, text, color):
        # Multiply base coordinates and dimensions by game_state.scale
        self.rect = pygame.Rect(int(x * game_state.scale), int(y * game_state.scale), int(width * game_state.scale), int(height * game_state.scale))
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        color = (min(self.color[0] + 30, 255), 
                min(self.color[1] + 30, 255), 
                min(self.color[2] + 30, 255)) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, int(2 * game_state.scale))  # Border scaled

        font = pygame.font.Font(None, get_scaled_font(36))
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
        # Scale all base values
        self.x = int(x * game_state.scale)
        self.y = int(y * game_state.scale)
        self.width = int(width * game_state.scale)
        self.height = int(height * game_state.scale)
        self.value = value  # a float between 0 and 1
        # Define knob dimensions (scaled)
        self.knob_width = int(10 * game_state.scale)
        self.knob_height = int((height + 4) * game_state.scale)
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
        pygame.draw.rect(screen, constants.BLACK, track_rect, int(2 * game_state.scale))  # scaled border

        # Calculate filled width based on current value
        filled_width = int(self.value * self.width)
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(screen, self.fill_color, filled_rect)
        
        # Calculate knob position (no border for the knob)
        knob_x = self.x + filled_width - self.knob_width // 2
        knob_y = self.y + (self.height - self.knob_height) // 2
        pygame.draw.rect(screen, self.knob_color, (knob_x, knob_y, self.knob_width, self.knob_height))
        pygame.draw.rect(screen, constants.BLACK, (knob_x, knob_y, self.knob_width, self.knob_height), int(2 * game_state.scale))

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
                save_music_settings(self.value)  # Save the new volume
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
            save_music_settings(self.value)  # Save the new volume

# Helper function to compute a shimmer effect surface for a rectangle.
def compute_shimmer_surface_for_tab_icon(rarity_color, rarity, width, height, phase):
    """
    Given a base color (tuple) and rarity (string), compute a shimmer surface
    of the specified width and height. 'phase' should be a float in [0,1].
    """
    # Convert the base color to a NumPy array
    base_color = np.array(rarity_color, dtype=np.float32)
    # Compute the "bright" color based on rarity.
    if rarity == "Exclusive":
        bright_color = np.minimum(base_color + 30, 255)
    else:
        bright_color = np.minimum(base_color + 70, 255)
    
    # Create coordinate grids for the given width/height.
    x_grid, y_grid = np.meshgrid(np.arange(width), np.arange(height))
    # Compute a diagonal coordinate between 0 and 1.
    diag = (x_grid / width + y_grid / height) / 2.0
    # Add phase (wrap around modulo 1)
    diag = (diag + phase) % 1.0
    # Compute blend: we want maximum brightness when diag is near 0.5.
    blend = np.abs(diag - 0.5) * 2  # 0 at center, 1 at edges.
    shimmer_width = 0.3  # Controls how narrow the bright band is.
    blend = 1 - np.clip(blend / shimmer_width, 0, 1)  # Now 1 means fully bright.
    blend = blend[:, :, None]  # Make it (height, width, 1) for broadcasting.
    
    # Compute final color at each pixel.
    pixel_array = base_color * (1 - blend) + bright_color * blend
    pixel_array = np.clip(pixel_array, 0, 255).astype(np.uint8)
    
    # Create a surface from the array.
    # Pygame expects shape (width, height, channels) so transpose axes.
    surface = pygame.surfarray.make_surface(np.transpose(pixel_array, (1, 0, 2)))
    return surface

class UpgradeButton(Button):
    RARITY_COLORS = {
        "Common": (144, 238, 144),
        "Rare": (135, 206, 250),
        "Epic": (186, 85, 211),
        "Mythic": (255, 71, 76),
        "Legendary": (255, 215, 0),
        "Exclusive": (255, 192, 203),
    }

    def __init__(self, x, y, width, height, upgrade, icon_image=None):
        # Scale the button coordinates and dimensions
        super().__init__(x, y, width, height, "", self.RARITY_COLORS.get(upgrade.Rarity, constants.GREEN))
        self.upgrade = upgrade
        self.icon_image = icon_image
        self.width = int(width * game_state.scale)
        self.height = int(height * game_state.scale)
        self.icon_size = int(64 * game_state.scale)
        self.circle_margin = int(10 * game_state.scale)
        self.rainbow_timer = 0  # Timer for the shimmer effect (in degrees)
        self.cooldown = 0  # Cooldown attribute

        # Precompute coordinate grids for vectorized shimmer computations
        # These grids remain constant for the button size.
        self._x_grid, self._y_grid = np.meshgrid(np.arange(self.width), np.arange(self.height))
        self.shimmer_width = 0.3  # Parameter for the falloff width

        # We'll cache a sequence of shimmer surfaces if needed.
        self.cached_shimmer = None
        self.cached_phase = None

    def draw(self, screen):
        # Update the timer. Increase by 4 degrees per frame and convert to a phase in [0,1]
        self.rainbow_timer = (self.rainbow_timer + 4) % 360
        phase = self.rainbow_timer / 360.0

        # Get the rarity color safely
        rarity_color = self.RARITY_COLORS.get(self.upgrade.Rarity, constants.GREEN)

        # Only recompute the shimmer effect if phase changed significantly
        if self.cached_shimmer is None or self.cached_phase is None or abs(phase - self.cached_phase) > 0.01:
            self.cached_shimmer = compute_shimmer_surface_for_tab_icon(
                rarity_color, self.upgrade.Rarity, self.width, self.height, phase
            )
            self.cached_phase = phase

        # Draw the cached shimmer surface onto the button's rectangle
        screen.blit(self.cached_shimmer, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, int(2 * game_state.scale))  # Border

        # Continue with the rest of the drawing (icon, text, etc.)
        font_name = pygame.font.Font(None, get_scaled_font(32))
        font_desc = pygame.font.Font(None, get_scaled_font(24))
        font_rarity = pygame.font.Font(None, get_scaled_font(20))

        # Draw the icon in a circle overlapping the top-left corner
        if self.icon_image:
            # Fixed icon size (scaled)
            icon_scaled = pygame.transform.scale(self.icon_image, (self.icon_size - int(34 * game_state.scale), self.icon_size - int(34 * game_state.scale)))

            # Calculate circle properties
            circle_radius = self.icon_size // 2 - int(5 * game_state.scale)
            circle_center = (self.rect.x + circle_radius - self.circle_margin - int(15 * game_state.scale), 
                             self.rect.y + circle_radius - self.circle_margin - int(15 * game_state.scale))

            # Draw circular background with button color and border
            pygame.draw.circle(screen, self.color, circle_center, circle_radius)
            pygame.draw.circle(screen, constants.BLACK, circle_center, circle_radius, int(2 * game_state.scale))  # Border

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
            if test_surface.get_width() <= self.width - int(20 * game_state.scale):  # 20px padding on each side
                current_line.append(word)
            else:
                if current_line:
                    title_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            title_lines.append(' '.join(current_line))

        # Render wrapped title text
        title_y = self.rect.y + int(20 * game_state.scale) + (self.icon_size - int(47 * game_state.scale))  # Space below the circle
        for line in title_lines:
            title_surface = font_name.render(line, True, constants.BLACK)
            title_rect = title_surface.get_rect(center=(self.rect.centerx, title_y))
            screen.blit(title_surface, title_rect)
            title_y += title_surface.get_height()

        # Render rarity below the title
        rarity_surface = font_rarity.render(self.upgrade.Rarity, True, constants.BLACK)
        rarity_rect = rarity_surface.get_rect(center=(self.rect.centerx, title_y - int(2 * game_state.scale)))
        screen.blit(rarity_surface, rarity_rect)

        # Centralized description text (with wrapping)
        desc_words = self.upgrade.description.split()
        desc_lines = []
        current_desc_line = []

        for word in desc_words:
            test_line = ' '.join(current_desc_line + [word])
            test_surface = font_desc.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - int(20 * game_state.scale):  # 20px padding on each side
                current_desc_line.append(word)
            else:
                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))
                current_desc_line = [word]
        if current_desc_line:
            desc_lines.append(' '.join(current_desc_line))

        # Render wrapped description text below rarity
        y_offset = rarity_rect.bottom + int(18 * game_state.scale)
        for line in desc_lines:
            desc_surface = font_desc.render(line, True, constants.BLACK)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(desc_surface, desc_rect)
            y_offset += desc_surface.get_height()

    def handle_event(self, event):
        if self.cooldown > 0:  # Check if the button is on cooldown
            return False  # Ignore events if on cooldown
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.cooldown = 30  # Set cooldown (e.g., 30 frames)
                return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1  # Decrease cooldown each frame

def draw_level_up_menu(screen):
    # Create semi-transparent overlay (dimensions already in screen coordinates)
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Get the number of upgrade choices the player should have
    num_choices = 3  # Default
    if any(upgrade.name == "+1 Upgrade Choice" for upgrade in game_state.player.applied_upgrades):
        num_choices = 4

    # Create menu panel - using proportional sizes and adjusting width based on number of choices
    base_panel_width = int(game_state.screen_width * 0.57)  # Base width for 3 choices
    panel_width = int(game_state.screen_width * (0.65 if num_choices == 3 else 0.85))  # Wider panel for 4 choices
    panel_height = int(game_state.screen_height * 0.4)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(2 * game_state.scale))

    # Level up text
    font = pygame.font.Font(None, get_scaled_font(48))
    text = font.render(f"Level {game_state.player.player_level} - Choose an Upgrade", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + int(50 * game_state.scale)))
    screen.blit(text, text_rect)

    # Create buttons if they don't exist
    if not hasattr(game_state, 'current_upgrade_buttons'):
        # Get random upgrades
        upgrade_pool = UpgradePool()
        upgrades = upgrade_pool.get_random_upgrades(num_choices, game_state.player)
        
        # Create buttons with proportional sizes
        button_width = int(game_state.screen_width * 0.18)  # ~16% of screen width
        button_height = int(game_state.screen_height * 0.2)  # ~15% of screen height
        button_spacing = int(game_state.screen_width * 0.023)  # ~2.6% of screen width
        
        # Calculate total width of all buttons and spacing
        total_width = (button_width * num_choices) + (button_spacing * (num_choices - 1))
        start_x = (game_state.screen_width - total_width) // 2

        game_state.current_upgrade_buttons = []
        for i, upgrade in enumerate(upgrades):
            x = start_x + (button_width + button_spacing) * i
            y = panel_y + int(150 * game_state.scale)
            icon_image = upgrade_pool.icon_images.get(upgrade.icon, None)
            button = UpgradeButton(x, y, button_width, button_height, upgrade, icon_image)
            game_state.current_upgrade_buttons.append(button)

    # Draw existing buttons
    for button in game_state.current_upgrade_buttons:
        button.update()  # Update button cooldown
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
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(2 * game_state.scale))

    # Pause menu text
    font = pygame.font.Font(None, get_scaled_font(48))
    text = font.render("Paused", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + int(50 * game_state.scale)))
    screen.blit(text, text_rect)

    # Initialize UI elements once
    if not hasattr(game_state, 'pause_ui'):
        # Button dimensions - proportional
        button_width = int(game_state.screen_width * 0.104)  # ~10.4% of screen width
        button_height = int(game_state.screen_height * 0.056)  # ~5.6% of screen height

        # Calculate positions for resume and quit buttons (already side by side)
        button_x = (game_state.screen_width - (button_width * 2 + int(game_state.screen_width * 0.01))) // 2
        button_y = panel_y + int(panel_height * 0.74)  # ~74% down the panel

        # Quit button (offset adjusted by scaling)
        quit_button = Button(button_x + button_width + int(20 * game_state.scale), button_y, button_width, button_height, "Quit", constants.RED)

        # Resume button
        resume_button = Button(button_x, button_y, button_width, button_height, "Resume", constants.GREEN)

        # Volume Slider - proportional
        slider_width = int(game_state.screen_width * 0.156)  # ~15.6% of screen width
        slider_height = int(game_state.screen_height * 0.019)  # ~1.9% of screen height
        slider_x = (game_state.screen_width - slider_width) // 2
        slider_y = panel_y + int(panel_height * 0.34)  # ~34% down the panel
        volume_slider = Slider(slider_x, slider_y, slider_width, slider_height, constants.music_volume)

        # Calculate positions for Upgrades and Stats buttons (side by side)
        buttons_spacing = int(20 * game_state.scale)  # spacing between buttons scaled
        total_width = button_width * 2 + buttons_spacing
        start_x = (game_state.screen_width - total_width) // 2
        upgrades_button = Button(start_x, slider_y + int(50 * game_state.scale), button_width, button_height, "Upgrades", constants.BLUE)
        stats_button = Button(start_x + button_width + buttons_spacing, slider_y + int(50 * game_state.scale), button_width, button_height, "Stats", constants.ORANGE)

        game_state.pause_ui = {
            'quit_button': quit_button,
            'resume_button': resume_button,
            'volume_slider': volume_slider,
            'upgrades_button': upgrades_button,
            'stats_button': stats_button
        }

    # Draw persistent elements
    game_state.pause_ui['quit_button'].draw(screen)
    game_state.pause_ui['resume_button'].draw(screen)
    game_state.pause_ui['volume_slider'].draw(screen)
    game_state.pause_ui['upgrades_button'].draw(screen)
    game_state.pause_ui['stats_button'].draw(screen)

    # Draw "Volume" label above the slider
    small_font = pygame.font.Font(None, get_scaled_font(30))
    volume_text = small_font.render("Volume", True, constants.BLACK)
    volume_text_rect = volume_text.get_rect(center=(game_state.screen_width // 2, panel_y + int(100 * game_state.scale)))
    screen.blit(volume_text, volume_text_rect)

    return (game_state.pause_ui['quit_button'],
            game_state.pause_ui['resume_button'],
            game_state.pause_ui['volume_slider'],
            game_state.pause_ui['upgrades_button'],
            game_state.pause_ui['stats_button'])

def draw_upgrades_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Constants for button dimensions
    button_width = int(game_state.screen_width * 0.22)
    button_height = int(game_state.screen_height * 0.046)
    button_spacing = int(game_state.screen_width * 0.01)  # Horizontal spacing

    # Use 70% of the screen height for the icon area
    max_column_height = int(game_state.screen_height * 0.75)
    title_height = int(game_state.screen_height * 0.037)
    close_button_height = int(game_state.screen_height * 0.046)

    # Calculate the number of upgrades
    num_upgrades = len(game_state.player.applied_upgrades)

    # Calculate total height for all buttons
    total_icon_height = (button_height * num_upgrades) + (button_spacing * (num_upgrades - 1))
    # Calculate the number of columns
    num_columns = math.ceil(total_icon_height / max_column_height) if total_icon_height > 0 else 1

    # Dynamic panel height based on the total icon height
    dynamic_panel_height = min(total_icon_height, max_column_height)
    panel_height = title_height + dynamic_panel_height + close_button_height + int(60 * game_state.scale)
    # Calculate panel width based on the number of columns
    panel_width = num_columns * (button_width + button_spacing)
    # Center the panel
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(2 * game_state.scale))

    # Draw title
    title_font = pygame.font.Font(None, get_scaled_font(36))
    title_surface = title_font.render("Obtained Upgrades", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + title_height // 2 + int(5 * game_state.scale)))
    screen.blit(title_surface, title_rect)

    # Draw upgrades
    phase = ((pygame.time.get_ticks() / 5) % 360) / 360.0
    column_width = button_width + button_spacing

    y_offset = panel_y + title_height + int(20 * game_state.scale)  # Starting Y position
    for i, upgrade in enumerate(game_state.player.applied_upgrades):
        column_index = i % num_columns
        row_index = i // num_columns

        x_offset = panel_x + column_index * column_width + (column_width - button_width) // 2
        current_y_offset = y_offset + row_index * (button_height + button_spacing) - int(10 * game_state.scale)

        rarity_color = UpgradeButton.RARITY_COLORS.get(upgrade.Rarity, constants.LIGHT_GREY)
        shimmer_surface = compute_shimmer_surface_for_tab_icon(rarity_color, upgrade.Rarity, button_width, button_height, phase)
        screen.blit(shimmer_surface, (x_offset, current_y_offset))

        pygame.draw.rect(screen, constants.BLACK, (x_offset, current_y_offset, button_width, button_height), int(2 * game_state.scale))

        # Draw upgrade name
        desc_font = pygame.font.Font(None, get_scaled_font(24))
        display_name = f"{upgrade.name} ({game_state.player.upgrade_levels.get(upgrade.name, 0)}x)"
        name_surface = desc_font.render(display_name, True, constants.BLACK)
        name_rect = name_surface.get_rect(center=(x_offset + button_width // 2, current_y_offset + button_height // 2))
        screen.blit(name_surface, name_rect)

    # Draw close button
    close_button_x = panel_x + (panel_width - int(100 * game_state.scale)) // 2
    close_button_y = panel_y + panel_height - close_button_height - int(20 * game_state.scale)
    close_button = Button(close_button_x, close_button_y, 100, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return close_button

def draw_stats_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Panel dimensions and positioning
    panel_width = int(game_state.screen_width * 0.45)
    panel_height = int(game_state.screen_height * 0.7)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel background and border
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(2 * game_state.scale))

    # Draw title at the top
    title_font = pygame.font.Font(None, get_scaled_font(36))
    title_surface = title_font.render("Player Stats", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + int(30 * game_state.scale)))
    screen.blit(title_surface, title_rect)

    # Define groups of stats with headers
    groups = [
        ("Basic Stats", [
            ("Level", f"{game_state.player.player_level:.1f}"),
            ("Experience", f"{game_state.player.player_experience:.1f}"),
            ("XP Gain Multiplier", f"{game_state.player.xp_gain_multiplier:.1f}"),
            ("Passive XP Gain (%)", f"{game_state.player.passive_xp_gain_percent_bonus:.1f}"),
            ("Speed", f"{game_state.player.speed:.1f}"),
            ("Damage Reduction (%)", f"{game_state.player.damage_reduction_percent_bonus:.1f}"),
        ]),
        ("Health Stats", [
            ("Health", f"{game_state.player.health:.1f}"),
            ("Max Health", f"{game_state.player.max_health:.1f}"),
            ("Health Regen (%)", f"{game_state.player.hp_regen:.1f}"),
            ("Health Regen Bonus (%)", f"{game_state.player.hp_regen_percent_bonus:.1f}"),
            ("Lifesteal (%)", f"{game_state.player.hp_steal:.1f}"),
        ]),
        ("Basic Bullet Stats", [
            ("Damage Multiplier", f"{game_state.player.base_damage_multiplier:.1f}"),
            ("Basic Bullet Damage Multiplier", f"{game_state.player.basic_bullet_damage_multiplier:.1f}"),
            ("Basic Bullet Speed Multiplier", f"{game_state.player.basic_bullet_speed_multiplier:.1f}"),
            ("Basic Bullet Piercing Multiplier", f"{ game_state.player.basic_bullet_piercing_multiplier:.1f}"),
            ("Basic Bullet Scales w/ Distance", f"{game_state.player.basic_bullet_scales_with_distance_travelled:.1f}"),
            ("Extra Projectiles/Shot", f"{game_state.player.basic_bullet_extra_projectiles_per_shot_bonus:.1f}"),
        ]),
        ("Random", [
            ("Roll the Dice Chance (%)", f"{game_state.player.random_upgrade_chance * 100:.1f}"),
        ]),
        ("Special Bullet Stats", [
            ("Special Bullet Damage Multiplier", f"{game_state.player.special_bullet_damage_multiplier:.1f}"),
            ("Special Bullet Speed Multiplier", f"{game_state.player.special_bullet_speed_multiplier:.1f}"),
            ("Special Bullet Piercing Multiplier", f"{game_state.player.special_bullet_piercing_multiplier:.1f}"),
            ("Special Bullet Radius Multiplier", f"{game_state.player.special_bullet_radius_multiplier:.1f}"),
            ("Special Bullet Can Repierce", f"{game_state.player.special_bullet_can_repierce:.1f}"),
            ("Special Bullet Scales w/ Dist", f"{game_state.player.special_bullet_scales_with_distance_travelled:.1f}"),
        ]),
        ("Pickup Stats", [
            ("Maximum Pickups", f"{game_state.player.max_pickups_on_screen:.1f}"),
            ("Pickup Heal Bonus (%)", f"{game_state.player.hp_pickup_healing_percent_bonus:.1f}"),
            ("Pickup Temp Damage Boost Duration (s)", f"{game_state.player.hp_pickup_damage_boost_duration_s:.1f}"),
            ("Pickup Temp Damage Boost (%)", f"{game_state.player.hp_pickup_damage_boost_percent_bonus:.1f}"),
            ("Pickup Permanent Health Boost (%)", f"{game_state.player.hp_pickup_permanent_hp_boost_percent_bonus:.1f}"),
            ("Pickup Permanent Damage Boost (%)", f"{game_state.player.hp_pickup_permanent_damage_boost_percent_bonus:.1f}"),
        ]),
        ("Special Bonus Stats", [
            ("Vengeful Special Bullet Dmg Bonus (%)", f"{game_state.player.percent_damage_taken_special_attack_bonus:.1f}"),
            ("Rage Bonus (%)", f"{game_state.player.rage_percent_bonus:.1f}"),
            ("Frenzy Bonus (%)", f"{game_state.player.frenzy_percent_bonus:.1f}"),
            ("Fear Bonus (%)", f"{game_state.player.fear_percent_bonus:.1f}"),
            ("Pride (No Damage Buff Requirement) (s)", f"{game_state.player.no_damage_buff_req_duration:.1f}"),
            ("Pride (No Damage Buff Multiplier)", f"{game_state.player.no_damage_buff_damage_bonus_multiplier:.1f}"),
        ]),
    ]

    # Set up fonts
    header_font = pygame.font.Font(None, get_scaled_font(32))
    header_font.set_underline(True)
    stat_font = pygame.font.Font(None, get_scaled_font(27))

    # Spacing and margin settings (scaled)
    top_margin = panel_y + int(70 * game_state.scale)  # space reserved at top (below title)
    bottom_margin = int(20 * game_state.scale)         # bottom margin before close button area
    left_margin = panel_x + int(20 * game_state.scale)
    column_spacing = int(15 * game_state.scale)

    # Calculate the maximum available vertical space for the columns
    available_height = (panel_y + panel_height) - bottom_margin - top_margin

    # First, compute each group’s height (header + each stat + intra-group spacing)
    group_heights = []
    group_spacing = int(15 * game_state.scale)  # extra space after each group
    for header, stat_list in groups:
        # header height plus a small gap
        h = header_font.get_linesize() + int(15 * game_state.scale)
        # add each stat line height plus a small gap
        for _name, _value in stat_list:
            h += stat_font.get_linesize() + int(5 * game_state.scale)
        # add extra spacing after the group
        h += group_spacing
        group_heights.append(h)

    # Now, greedily distribute groups into columns so that the total height in each column <= available_height
    columns = []   # each column is a list of group indices
    current_column = []
    current_height = 0

    for i, group_h in enumerate(group_heights):
        if current_height + group_h > available_height and current_column:
            # Start a new column if this group doesn't fit in the current column
            columns.append(current_column)
            current_column = [i]
            current_height = group_h
        else:
            current_column.append(i)
            current_height += group_h
    if current_column:
        columns.append(current_column)

    # Determine column width (distribute available width evenly)
    available_width = panel_width - int(40 * game_state.scale)  # leaving some left/right margins
    num_columns = len(columns)
    column_width = (available_width - (num_columns - 1) * column_spacing) // num_columns

    # Draw the groups in each column
    for col_index, group_indices in enumerate(columns):
        # X position for this column
        col_x = left_margin + col_index * (column_width + column_spacing)
        current_y = top_margin  # start at the top margin for each column

        for i in group_indices:
            header, stat_list = groups[i]
            # Render header
            header_surface = header_font.render(header, True, constants.BLACK)
            screen.blit(header_surface, (col_x, current_y))
            current_y += header_font.get_linesize() + int(2 * game_state.scale)

            # Render each stat line (indented slightly)
            for name, value in stat_list:
                stat_text = f"{name}: {value}"
                stat_surface = stat_font.render(stat_text, True, constants.BLACK)
                screen.blit(stat_surface, (col_x + int(10 * game_state.scale), current_y))
                current_y += stat_font.get_linesize() + int(5 * game_state.scale)

            # Extra space after group
            current_y += group_spacing

    # Draw the close button at the bottom center of the panel
    close_button_width = int(100 * game_state.scale)
    close_button_height = int(game_state.screen_height * 0.046 * game_state.scale)
    close_button_x = panel_x + (panel_width - close_button_width) // 2
    close_button_y = panel_y + panel_height - close_button_height - int(20 * game_state.scale)
    close_button = Button(close_button_x, close_button_y, close_button_width, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return close_button
