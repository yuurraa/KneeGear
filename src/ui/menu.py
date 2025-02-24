import pygame
import numpy as np
from src.engine.helpers import get_design_mouse_pos, get_text_scaling_factor, get_ui_scaling_factor
from src.engine.music_handler import save_music_settings
import src.engine.constants as constants
import src.engine.game_state as game_state
import math
import random

def darken_color(color, factor=0.61):
    """Return a version of color darkened by the given factor (0 to 1)."""
    r, g, b = color
    return (max(0, int(r * factor)),
            max(0, int(g * factor)),
            max(0, int(b * factor)))

ui_scaling_factor = get_ui_scaling_factor()
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        # Draw the button background and border first.
        current_color = darken_color(self.color, 0.61) if self.hover else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, 2)
        
        # Now draw the button text on top.
        font = pygame.font.Font(None, get_text_scaling_factor(36))
        text_surface = font.render(self.text, True, constants.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            self.hover = self.rect.collidepoint(design_mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            if self.rect.collidepoint(design_mouse_pos):
                return True
        return False

class IconButton:
    def __init__(self, x, y, width, height, image, bg_color=constants.WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.bg_color = bg_color  # Original background color
        self.hover = False

    def draw(self, screen):
        # If hovering, darken the background color
        bg_color = (max(self.bg_color[0] - 40, 0),
                    max(self.bg_color[1] - 40, 0),
                    max(self.bg_color[2] - 40, 0)) if self.hover else self.bg_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, constants.BLACK, self.rect, width=2, border_radius=8)
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, image_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            self.hover = self.rect.collidepoint(design_mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            if self.rect.collidepoint(design_mouse_pos):
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
            design_mouse_pos = get_design_mouse_pos(event.pos)
            
            # Calculate knob's x position based on current value
            knob_x = self.x + (self.value * (self.width - self.knob_width))
            # Create knob rect
            knob_rect = pygame.Rect(
                knob_x,
                self.y + self.height // 2 - self.knob_height // 2,
                self.knob_width,
                self.knob_height
            )
            # Also create a rect for the slider track
            track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if knob_rect.collidepoint(design_mouse_pos) or track_rect.collidepoint(design_mouse_pos):
                self.dragging = True
                # Update position if clicked on track
                mouse_x = design_mouse_pos[0]
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
            design_mouse_pos = get_design_mouse_pos(event.pos)
            mouse_x = design_mouse_pos[0]
            new_knob_x = max(
                self.x,
                min(mouse_x - self.knob_width / 2, self.x + self.width - self.knob_width)
            )
            self.value = (new_knob_x - self.x) / (self.width - self.knob_width)
            constants.music_volume = self.value
            pygame.mixer.music.set_volume(self.value)
            save_music_settings(self.value)  # Save the new volume

# Global caches
_grid_cache = {}          # For coordinate grids (both raw and normalized)
_shimmer_cache = {}       # For computed shimmer surfaces keyed by parameters
LOW_RES_FACTOR = 2

def get_coordinate_grids(width, height):
    """Cache raw coordinate grids for given dimensions."""
    key = ("raw", width, height)
    if key not in _grid_cache:
        x_grid, y_grid = np.meshgrid(np.arange(width), np.arange(height))
        _grid_cache[key] = (x_grid, y_grid)
    return _grid_cache[key]

def get_normalized_grid(width, height):
    """Return a precomputed normalized grid based on raw grids."""
    key = ("norm", width, height)
    if key not in _grid_cache:
        x_grid, y_grid = get_coordinate_grids(width, height)
        # Normalized so that each coordinate lies in [0,1]
        norm_grid = (x_grid / width + y_grid / height) / 2.0
        _grid_cache[key] = norm_grid
    return _grid_cache[key]

def quantize_phase(phase, step=0.025):
    """Quantize phase to reduce the number of unique surfaces computed."""
    return round(phase / step) * step

def compute_shimmer_surface_for_tab_icon(rarity_color, rarity, width, height, phase, surface=None):
    # Determine low resolution dimensions
    low_width, low_height = width // LOW_RES_FACTOR, height // LOW_RES_FACTOR

    # Optional: create a cache key based on parameters (including quantized phase)
    q_phase = quantize_phase(phase)
    cache_key = (rarity_color, rarity, low_width, low_height, q_phase)
    if cache_key in _shimmer_cache:
        cached_surf = _shimmer_cache[cache_key]
        # Scale up to full size and return
        return pygame.transform.smoothscale(cached_surf, (width, height))

    # Get the precomputed normalized grid
    norm_grid = get_normalized_grid(low_width, low_height)

    # Compute the shifted grid based on phase (only need to do modulo on the precomputed grid)
    diag = (norm_grid + phase) % 1.0

    # Compute blend factor for shimmer effect
    blend = np.abs(diag - 0.5) * 2  
    shimmer_width = 0.3  
    blend = 1 - np.clip(blend / shimmer_width, 0, 1)
    blend = blend[:, :, None]  # Add a channel axis

    # Precompute base and bright colors (as float32 arrays)
    base_color = np.array(rarity_color, dtype=np.float32)
    bright_offset = 30 if rarity == "Exclusive" else 70
    bright_color = np.minimum(base_color + bright_offset, 255)

    # Compute the final pixel array
    pixel_array = base_color * (1 - blend) + bright_color * blend
    pixel_array = np.clip(pixel_array, 0, 255).astype(np.uint8)

    # Create or update the low-res surface
    if surface is None:
        surface = pygame.Surface((low_width, low_height))
    pygame.surfarray.blit_array(surface, np.transpose(pixel_array, (1, 0, 2)))

    # Cache the computed low-res surface
    _shimmer_cache[cache_key] = surface.copy()

    # Scale up to full size before returning
    return pygame.transform.smoothscale(surface, (width, height))

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
        super().__init__(x, y, width, height, "", self.RARITY_COLORS.get(upgrade.Rarity, constants.GREEN))
        self.upgrade = upgrade
        self.icon_image = icon_image
        self.width = width
        self.height = height
        self.icon_size = 64
        self.circle_margin = 10
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
        # Update the timer and compute the phase for the shimmer effect
        self.rainbow_timer = (self.rainbow_timer + 4) % 360
        phase = self.rainbow_timer / 360.0

        # Get the rarity color safely
        rarity_color = self.RARITY_COLORS.get(self.upgrade.Rarity, constants.GREEN)

        # Recompute the shimmer effect if needed
        if self.cached_shimmer is None or self.cached_phase is None or abs(phase - self.cached_phase) > 0.01:
            self.cached_shimmer = compute_shimmer_surface_for_tab_icon(
                rarity_color, self.upgrade.Rarity, self.width, self.height, phase
            )
            self.cached_phase = phase

        # Draw the cached shimmer background and border
        screen.blit(self.cached_shimmer, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, 2)
        
        if self.hover:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 40))  # Alpha=25 for subtle darkening
            screen.blit(overlay, self.rect.topleft)
            
        # Continue with drawing the rest (icon, text, etc.)
        font_name = pygame.font.Font(None, get_text_scaling_factor(32))
        font_desc = pygame.font.Font(None, get_text_scaling_factor(24))
        font_rarity = pygame.font.Font(None, get_text_scaling_factor(20))

        # Draw the icon in a circle overlapping the top-left corner
        if self.icon_image:
            icon_scaled = pygame.transform.scale(self.icon_image, (self.icon_size - 34, self.icon_size - 34))
            circle_radius = self.icon_size // 2 - 5
            circle_center = (self.rect.x + circle_radius - self.circle_margin - 15, 
                            self.rect.y + circle_radius - self.circle_margin - 15)
            pygame.draw.circle(screen, self.color, circle_center, circle_radius)
            pygame.draw.circle(screen, constants.BLACK, circle_center, circle_radius, 2)
            icon_rect = icon_scaled.get_rect(center=circle_center)
            screen.blit(icon_scaled, icon_rect)

        # Draw centralized wrapped title text
        words = self.upgrade.name.split()
        title_lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font_name.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    title_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            title_lines.append(' '.join(current_line))

        title_y = self.rect.y + 20 + (self.icon_size - 47) + getattr(self, "title_offset", 0)
        for line in title_lines:
            title_surface = font_name.render(line, True, constants.BLACK)
            title_rect = title_surface.get_rect(center=(self.rect.centerx, title_y))
            screen.blit(title_surface, title_rect)
            title_y += title_surface.get_height()

        # Render rarity text below the title
        rarity_surface = font_rarity.render(self.upgrade.Rarity, True, constants.BLACK)
        rarity_rect = rarity_surface.get_rect(center=(self.rect.centerx, title_y - 2))
        screen.blit(rarity_surface, rarity_rect)

        # Render centralized wrapped description text below rarity
        desc_words = self.upgrade.description.split()
        desc_lines = []
        current_desc_line = []
        for word in desc_words:
            test_line = ' '.join(current_desc_line + [word])
            test_surface = font_desc.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - 20:
                current_desc_line.append(word)
            else:
                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))
                current_desc_line = [word]
        if current_desc_line:
            desc_lines.append(' '.join(current_desc_line))

        y_offset = rarity_rect.bottom + 18
        for line in desc_lines:
            desc_surface = font_desc.render(line, True, constants.BLACK)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(desc_surface, desc_rect)
            y_offset += desc_surface.get_height()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            self.hover = self.rect.collidepoint(design_mouse_pos)
        if self.cooldown > 0:  # Check if the button is on cooldown
            return False  # Ignore events if on cooldown
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Convert screen coordinates to design coordinates.
            design_mouse_pos = get_design_mouse_pos(event.pos)
            if self.rect.collidepoint(design_mouse_pos):
                self.cooldown = 30  # Set cooldown (e.g., 30 frames)
                return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1  # Decrease cooldown each frame
            
def generate_shades(base_color, variation=30):
    """Generate a random shade of the given base color with slight variation."""
    r, g, b = base_color
    return (
        max(0, min(255, r + random.randint(-variation, variation))),
        max(0, min(255, g + random.randint(-variation, variation))),
        max(0, min(255, b + random.randint(-variation, variation)))
    )

class Particle:
    def __init__(self, pos, base_color):
        self.pos = list(pos)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.radius = random.randint(5, 8)
        self.lifetime = random.randint(40, 60)
        # Generate a dynamic shade of the base color
        self.color = generate_shades(base_color)

    def update(self):
        # Move the particle.
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        # Decrease lifetime.
        self.lifetime -= 1
        # Gradually shrink the particle.
        self.radius = max(0, self.radius - 0.1)

    def draw(self, screen):
        if self.lifetime > 0 and self.radius > 0:
            # Create a small surface for the particle.
            diameter = int(self.radius * 8)
            particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))

class SkinButton(UpgradeButton):
    def __init__(self, x, y, width, height, skin_name, skin_rarity, icon_image=None):
        # Create a dummy upgrade to pass to the base class.
        class DummySkinUpgrade:
            def __init__(self, name, rarity):
                self.name = name
                self.Rarity = rarity
                self.description = ""
        dummy_upgrade = DummySkinUpgrade(skin_name, skin_rarity)
        super().__init__(x, y, width, height, dummy_upgrade, icon_image)
        
        self.glow_timer = 0  # Animates from 0 up to 500 when selected.
        self.skin_id = None  # Use skin_id instead of skin_index.
        self.pulse_phase = 0   # For the pulsing (scaling) effect.
        self.particles = []    # List to hold particle effects.
        self.title_offset = -5

    def trigger_glow(self):
        # Reset the glow timer and pulse phase for a fade-in and pulse effect.
        self.glow_timer = 0
        self.pulse_phase = 0

    def draw(self, screen):
        # Determine if this skin is currently selected by comparing IDs.
        selected = (hasattr(self, 'skin_id') and game_state.player.current_skin_id == self.skin_id)
        
        # Base settings for the glow effect
        base_glow_padding = 9      # Padding around the button for the glow.
        fade_speed = 50            # Speed for fade in/out.
        
        if self.hover:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 40))  # Alpha=25 for subtle darkening
            screen.blit(overlay, self.rect.topleft)
        
        # Animate the glow timer: fade in when selected, fade out otherwise.
        if selected:
            if self.glow_timer < 500:
                self.glow_timer = min(self.glow_timer + fade_speed, 500)
            # Only pulse when fully faded in.
            if self.glow_timer >= 500:
                self.pulse_phase += 0.075  # Adjust the pulse speed here.
        else:
            if self.glow_timer > 0:
                self.glow_timer = max(self.glow_timer - fade_speed, 0)
        
        # Base glow dimensions.
        glow_width = self.rect.width + base_glow_padding * 2
        glow_height = self.rect.height + base_glow_padding * 2

        # Apply the scaling (pulsing) effect.
        pulse_scale = 1.0
        if selected and self.glow_timer >= 500:
            # Oscillates between ~0.9 and 1.1.
            pulse_scale = 1.0 + 0.023 * math.sin(self.pulse_phase)
        scaled_glow_width = int(glow_width * pulse_scale)
        scaled_glow_height = int(glow_height * pulse_scale)
        
        # Only draw the glow if there's an effect.
        if self.glow_timer > 0:
            # Create a surface for the glow.
            glow_surface = pygame.Surface((scaled_glow_width, scaled_glow_height), pygame.SRCALPHA)
            # Compute alpha proportionally (max alpha = 200).
            alpha = int(200 * (self.glow_timer / 500))
            glow_color = (self.color[0], self.color[1], self.color[2], alpha)
            
            # Draw a rounded rectangle on the glow surface.
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=int(12 * pulse_scale))
            
            # Center the glow around the button.
            glow_rect = glow_surface.get_rect(center=self.rect.center)
            screen.blit(glow_surface, glow_rect)
        
        # Particle Effects: spawn particles when the skin is selected and fully faded in.
        if selected and self.glow_timer >= 500:
            # Spawn a new particle with some probability each frame.
            if random.random() < 1:  # Adjust spawn rate as needed.
                # Randomize the spawn position near the button's center.
                particle_pos = (
                    self.rect.centerx + random.uniform(-self.rect.width/2, self.rect.width/2),
                    self.rect.centery + random.uniform(-self.rect.height/2, self.rect.height/2)
                )
                self.particles.append(Particle(particle_pos, self.color))
        
        # Update and draw all active particles.
        for particle in self.particles:
            particle.update()
            particle.draw(screen)
        # Remove expired particles.
        self.particles = [p for p in self.particles if p.lifetime > 0 and p.radius > 0]
        
        # Draw the base button content (shimmer, text, icon)
        super().draw(screen)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = get_design_mouse_pos(event.pos)
            self.hover = self.rect.collidepoint(design_mouse_pos)
        return super().handle_event(event)


def draw_level_up_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Get the number of upgrade choices the player should have
    num_choices = 3  # Default
    if any(upgrade.name == "+1 Upgrade Choice" for upgrade in game_state.player.applied_upgrades):
        num_choices = 4

    # Create menu panel - using proportional sizes and adjusting width based on number of choices
    panel_width = int(game_state.screen_width * (0.65 if num_choices == 3 else 0.85))  # Wider panel for 4 choices
    panel_height = int(game_state.screen_height * 0.4)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Level up text
    font = pygame.font.Font(None, get_text_scaling_factor(48))
    text = font.render(f"Level {game_state.player.player_level} - Choose an Upgrade", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + 50))
    screen.blit(text, text_rect)

    # Create buttons if they don't exist
    if not hasattr(game_state, 'current_upgrade_buttons'):
        # Get random upgrades
        from src.player.upgrades import UpgradePool
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
            y = panel_y + 150
            icon_image = upgrade_pool.icon_images.get(upgrade.icon, None)
            button = UpgradeButton(x, y, button_width, button_height, upgrade, icon_image)
            game_state.current_upgrade_buttons.append(button)

    # Draw existing buttons
    for button in game_state.current_upgrade_buttons:
        button.update()  # Update button cooldown
        button.draw(screen)

    return (game_state.current_upgrade_buttons)

def draw_pause_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create menu panel with proportional sizes
    panel_width = int(game_state.screen_width * 0.29 * ui_scaling_factor)
    panel_height = int(game_state.screen_height * 0.35 * ui_scaling_factor)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Pause menu title
    font = pygame.font.Font(None, get_text_scaling_factor(48))
    text = font.render("Pause Menu", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + int(50 * ui_scaling_factor)))
    screen.blit(text, text_rect)
    
    # Standard icon size and padding
    icon_size = int(35 * ui_scaling_factor) - 3
    icon_padding = int(10 * ui_scaling_factor)
    
    # Slider dimensions (adjusted length)
    slider_width = int((panel_width - (icon_size + 2 * icon_padding)) * 0.8)
    slider_height = int(game_state.screen_height * 0.019)
    slider_y = panel_y + int(90 * ui_scaling_factor)
    
    # --- Center the Volume Icon and Slider as a Group ---
    # Calculate total width of the volume group (icon + padding + slider)
    total_volume_width = icon_size + icon_padding + slider_width
    # Determine the starting x so the group is centered within the panel
    group_start_x = panel_x + (panel_width - total_volume_width) // 2
    volume_icon_x = group_start_x
    slider_x = group_start_x + icon_size + icon_padding

    music_bar_y = slider_y + int(50 * ui_scaling_factor)
    buttons_y = music_bar_y + int(45 * ui_scaling_factor)

    # Initialize UI elements if not already created
    if not hasattr(game_state, 'pause_ui'):
        button_width = int(game_state.screen_width * 0.104)
        button_height = int(game_state.screen_height * 0.056)
        button_x = (game_state.screen_width - (button_width * 2 + int(game_state.screen_width * 0.01))) // 2
        buttons_spacing = 20 * ui_scaling_factor

        volume_slider = Slider(slider_x, slider_y, slider_width, slider_height, constants.music_volume)

        upgrades_button = Button(button_x, buttons_y, button_width, button_height, "Upgrades", constants.BLUE)
        stats_button = Button(button_x + button_width + buttons_spacing, buttons_y, button_width, button_height, "Stats", constants.ORANGE)
        resume_button = Button(button_x, buttons_y + button_height + buttons_spacing, button_width, button_height, "Resume", constants.GREEN)
        quit_button = Button(button_x + button_width + buttons_spacing, buttons_y + button_height + buttons_spacing, button_width, button_height, "Quit", constants.RED)

        game_state.pause_ui = {
            'quit_button': quit_button,
            'resume_button': resume_button,
            'volume_slider': volume_slider,
            'upgrades_button': upgrades_button,
            'stats_button': stats_button
        }

    # ---- NEW: Music Control Bar UI ----
    if not hasattr(game_state, 'pause_music_ui'):
        music_bar_margin = 25
        music_bar_width = panel_width - (2 * music_bar_margin)
        music_bar_x = panel_x + music_bar_margin
        music_bar_y = panel_y + int(121 * ui_scaling_factor)

        btn_size = icon_size

        playlist_icon = pygame.image.load("assets/ui/playlist.png").convert_alpha()
        previous_icon = pygame.image.load("assets/ui/previous.png").convert_alpha()
        next_icon = pygame.image.load("assets/ui/next.png").convert_alpha()

        playlist_icon = pygame.transform.scale(playlist_icon, (icon_size, icon_size))
        previous_icon = pygame.transform.scale(previous_icon, (icon_size - 9, icon_size - 9))
        next_icon = pygame.transform.scale(next_icon, (icon_size - 9, icon_size - 9))

        playlist_button = IconButton(music_bar_x, music_bar_y, btn_size, btn_size, image=playlist_icon)
        previous_button = IconButton(music_bar_x + btn_size + 5, music_bar_y, btn_size, btn_size, image=previous_icon)
        next_button = IconButton(music_bar_x + music_bar_width - btn_size + 5, music_bar_y, btn_size, btn_size, image=next_icon)
        
        song_display_x = music_bar_x + (2 * btn_size + 20) - 5
        song_display_width = music_bar_width - (3 * btn_size + 20)
        song_display_rect = pygame.Rect(song_display_x, music_bar_y, song_display_width, btn_size)
        
        game_state.pause_music_ui = {
            'playlist_button': playlist_button,
            'previous_button': previous_button,
            'next_button': next_button,
            'song_display_rect': song_display_rect
        }

    # Draw the persistent pause UI
    game_state.pause_ui['quit_button'].draw(screen)
    game_state.pause_ui['resume_button'].draw(screen)
    game_state.pause_ui['volume_slider'].draw(screen)
    game_state.pause_ui['upgrades_button'].draw(screen)
    game_state.pause_ui['stats_button'].draw(screen)

    # ---- Draw Volume Icon ----
    volume_icon = pygame.image.load("assets/ui/volume.png").convert_alpha()
    volume_icon = pygame.transform.scale(volume_icon, (icon_size, icon_size))
    volume_icon_y = slider_y + (slider_height - icon_size) // 2
    screen.blit(volume_icon, (volume_icon_x, volume_icon_y))

    # ---- Draw Music Bar ----
    music_ui = game_state.pause_music_ui
    music_ui['playlist_button'].draw(screen)
    music_ui['previous_button'].draw(screen)
    music_ui['next_button'].draw(screen)
    
    pygame.draw.rect(screen, constants.LIGHT_GREY, music_ui['song_display_rect'])
    pygame.draw.rect(screen, constants.BLACK, music_ui['song_display_rect'], 2)
    
    current_song_display = getattr(game_state, 'current_song_display', "No Song")
    song_font = pygame.font.Font(None, get_text_scaling_factor(24))
    text_surface = song_font.render(current_song_display, True, constants.BLACK)
    
    padding = 30  
    ticker_width = text_surface.get_width() + padding

    display_rect = music_ui['song_display_rect']
    display_width = display_rect.width
    display_height = display_rect.height

    if not hasattr(game_state, "song_ticker_offset"):
        game_state.song_ticker_offset = 0.0

    game_state.song_ticker_offset += 0.5  
    if game_state.song_ticker_offset >= ticker_width:
        game_state.song_ticker_offset -= ticker_width

    center_y = display_rect.y + (display_height - text_surface.get_height()) // 2

    previous_clip = screen.get_clip()
    screen.set_clip(display_rect)

    start_x = -game_state.song_ticker_offset
    while start_x < display_width:
        screen.blit(text_surface, (display_rect.x + start_x, center_y))
        start_x += ticker_width

    screen.set_clip(previous_clip)

    return (game_state.pause_ui['quit_button'],
            game_state.pause_ui['resume_button'],
            game_state.pause_ui['volume_slider'],
            game_state.pause_ui['upgrades_button'],
            game_state.pause_ui['stats_button'],
            game_state.pause_music_ui['playlist_button'],
            game_state.pause_music_ui['previous_button'],
            game_state.pause_music_ui['next_button'])

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

    # Use 75% of the screen height for the icon area
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
    panel_height = title_height + dynamic_panel_height + close_button_height + 60

    # Calculate panel width based on the number of columns
    panel_width = num_columns * (button_width + button_spacing)

    # Center the panel
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw title
    title_font = pygame.font.Font(None, get_text_scaling_factor(36))
    title_surface = title_font.render("Obtained Upgrades", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + title_height // 2 + 5))
    screen.blit(title_surface, title_rect)

    # Draw upgrades
    phase = ((pygame.time.get_ticks() / 5) % 360) / 360.0
    column_width = button_width + button_spacing

    y_offset = panel_y + title_height + 20  # Starting Y position
    for i, upgrade in enumerate(game_state.player.applied_upgrades):
        column_index = i % num_columns
        row_index = i // num_columns

        x_offset = panel_x + column_index * column_width + (column_width - button_width) // 2
        current_y_offset = y_offset + row_index * (button_height + button_spacing) - 10

        rarity_color = UpgradeButton.RARITY_COLORS.get(upgrade.Rarity, constants.LIGHT_GREY)
        shimmer_surface = compute_shimmer_surface_for_tab_icon(rarity_color, upgrade.Rarity, button_width, button_height, phase)
        screen.blit(shimmer_surface, (x_offset, current_y_offset))

        pygame.draw.rect(screen, constants.BLACK, (x_offset, current_y_offset, button_width, button_height), 2)

        # Draw upgrade name
        desc_font = pygame.font.Font(None, get_text_scaling_factor(24))
        display_name = f"{upgrade.name} ({game_state.player.upgrade_levels.get(upgrade.name, 0)}x)"
        name_surface = desc_font.render(display_name, True, constants.BLACK)
        name_rect = name_surface.get_rect(center=(x_offset + button_width // 2, current_y_offset + button_height // 2))
        screen.blit(name_surface, name_rect)

    # Draw close button
    close_button_x = panel_x + (panel_width - 100) // 2
    close_button_y = panel_y + panel_height - close_button_height - 20
    close_button = Button(close_button_x, close_button_y, 100, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (close_button)

def draw_stats_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Panel dimensions and positioning
    panel_width = int(game_state.screen_width * 0.44)
    panel_height = int(game_state.screen_height * 0.7)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel background and border
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw title at the top
    title_font = pygame.font.Font(None, get_text_scaling_factor(36))
    title_surface = title_font.render("Player Stats", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
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
            ("Basic Bullet Piercing Multiplier", f"{game_state.player.basic_bullet_piercing_multiplier:.1f}"),
            ("Basic Bullet Scales w/ Distance", f"{game_state.player.basic_bullet_scales_with_distance_travelled:.1f}"),
            ("Extra Projs/Shot", f"{game_state.player.basic_bullet_extra_projectiles_per_shot_bonus:.1f}"),
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
            ("Pride (No Damage Buff Req) (s)", f"{game_state.player.no_damage_buff_req_duration:.1f}"),
            ("Pride (No Damage Buff Mult)", f"{game_state.player.no_damage_buff_damage_bonus_multiplier:.1f}"),
        ]),
    ]

    # Set up fonts
    header_font = pygame.font.Font(None, get_text_scaling_factor(25 * ui_scaling_factor))
    header_font.set_underline(True)
    stat_font = pygame.font.Font(None, get_text_scaling_factor(20 * ui_scaling_factor))

    # Spacing and margin settings
    top_margin = panel_y + 70  # space reserved at top (below title)
    bottom_margin = 20         # bottom margin before close button area
    left_margin = panel_x + 20
    column_spacing = 15

    # Calculate the maximum available vertical space for the columns
    available_height = panel_y + panel_height - bottom_margin - top_margin

    # First, compute each group's height (header + each stat + intra-group spacing)
    group_heights = []
    group_spacing = 15  # extra space after each group
    for header, stat_list in groups:
        # header height plus a small gap
        h = header_font.get_linesize() + 15
        # add each stat line height plus a small gap
        for _name, _value in stat_list:
            h += stat_font.get_linesize() + 5
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
    available_width = panel_width - 40  # leaving some left/right margins
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
            current_y += header_font.get_linesize() + 2

            # Render each stat line (indented slightly)
            for name, value in stat_list:
                stat_text = f"{name}: {value}"
                stat_surface = stat_font.render(stat_text, True, constants.BLACK)
                screen.blit(stat_surface, (col_x + 10, current_y))
                current_y += stat_font.get_linesize() + 5

            # Extra space after group
            current_y += group_spacing

    # Draw the close button at the bottom center of the panel
    close_button_width = 100
    close_button_height = int(game_state.screen_height * 0.046)
    close_button_x = panel_x + (panel_width - close_button_width) // 2
    close_button_y = panel_y + panel_height - close_button_height - 20
    close_button = Button(close_button_x, close_button_y, close_button_width, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (close_button)

def draw_main_menu(screen):
    # Create a semi-transparent overlay for the menu
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.WHITE)
    overlay.set_alpha(255)
    screen.blit(overlay, (0, 0))

    # Draw menu title
    font = pygame.font.Font(None, get_text_scaling_factor(100))
    title_text = font.render("Gooner Game", True, constants.BLACK)
    title_rect = title_text.get_rect(center=(game_state.screen_width // 2, game_state.screen_height // 2 - 100))
    screen.blit(title_text, title_rect)

    # Draw Start Game button
    start_button = Button(game_state.screen_width // 2 - 100, game_state.screen_height // 2, 200, 50, "Start Game", constants.GREEN)
    start_button.draw(screen)

    # Draw Skin Selection button
    skin_button = Button(game_state.screen_width // 2 - 100, game_state.screen_height // 2 + 60, 200, 50, "Select Skin", constants.BLUE)
    skin_button.draw(screen)

    # Draw Quit button
    quit_button = Button(game_state.screen_width // 2 - 100, game_state.screen_height // 2 + 120, 200, 50, "Quit", constants.RED)
    quit_button.draw(screen)
    
    version_font = pygame.font.Font(None, get_text_scaling_factor(24))
    version_text = version_font.render("v0.1.3 - (WIP)", True, constants.BLACK)
    version_rect = version_text.get_rect(bottomright=(game_state.screen_width - 10, game_state.screen_height - 10))
    screen.blit(version_text, version_rect)

    return (start_button, quit_button, skin_button)

def draw_skin_selection_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.WHITE)
    overlay.set_alpha(255)
    screen.blit(overlay, (0, 0))

    # Draw title
    title_font = pygame.font.Font(None, get_text_scaling_factor(72))
    title_surface = title_font.render("Select Your Skin", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(game_state.screen_width // 2, 50))
    screen.blit(title_surface, title_rect)

    # Button dimensions
    button_width = int(game_state.screen_width * 0.15)
    button_height = int(game_state.screen_height * 0.075)
    button_spacing = 20

    # Draw available skins as buttons with shimmer effect.
    # NOTE: If game_state.player.skins is now a dictionary, iterate over its values.
    skin_buttons = []
    for skin in game_state.player.skins.values():
        button_x = (game_state.screen_width - button_width) // 2
        button_y = 100 + (button_height + button_spacing) * len(skin_buttons)
      
        # Then draw the black border
        pygame.draw.rect(screen, constants.BLACK, (button_x, button_y, button_width, button_height), 2)
        
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
    close_button_y = game_state.screen_height - close_button_height - 30
    close_button = Button(close_button_x, close_button_y, close_button_width, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (skin_buttons, close_button)
