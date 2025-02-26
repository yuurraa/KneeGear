import pygame
import random
import numpy as np
import math
from typing import Optional

import src.engine.constants as constants
import src.engine.game_state as game_state
from src.engine.helpers import get_ui_scaling_factor, compute_shimmer_surface_for_tab_icon, draw_hover_overlay
from src.ui.components.ui_particles import Particle

ui_scaling_factor = get_ui_scaling_factor()


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        # Update hover state based on current mouse position
        design_mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(design_mouse_pos)
        
        # Draw the button background and border.
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, int(4 * ui_scaling_factor))
        
        # Draw the button text.
        text_surface = game_state.FONTS["medium"].render(self.text, True, constants.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        if self.hover:
            draw_hover_overlay(screen, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = pygame.mouse.get_pos()
            self.hover = self.rect.collidepoint(design_mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            design_mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(design_mouse_pos):
                return True
        return False


class IconButton:
    def __init__(self, x, y, width, height, image, bg_color=constants.LIGHT_GREY):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.bg_color = bg_color  # Original background color
        self.hover = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, width=int(4 * ui_scaling_factor))
        image_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, image_rect)
        if self.hover:
            draw_hover_overlay(screen, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = pygame.mouse.get_pos()
            self.hover = self.rect.collidepoint(design_mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            design_mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(design_mouse_pos):
                return True
        return False


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
        # Update hover state based on current mouse position.
        design_mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(design_mouse_pos)
        
        # Update timer and compute shimmer phase.
        self.rainbow_timer = (self.rainbow_timer + 4) % 360
        phase = self.rainbow_timer / 360.0
        
        # Get rarity color safely.
        rarity_color = self.RARITY_COLORS.get(self.upgrade.Rarity, constants.GREEN)
        
        # Recompute shimmer effect if needed.
        if self.cached_shimmer is None or self.cached_phase is None or abs(phase - self.cached_phase) > 0.01:
            self.cached_shimmer = compute_shimmer_surface_for_tab_icon(
                rarity_color, self.upgrade.Rarity, self.width, self.height, phase
            )
            self.cached_phase = phase
        
        # Draw the cached shimmer background and border.
        screen.blit(self.cached_shimmer, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, int(4 * ui_scaling_factor))
        
        # Variables for icon drawing.
        icon_circle_center = None
        icon_circle_radius = None

        if self.icon_image:
            icon_scaled = pygame.transform.scale(
                self.icon_image,
                (self.icon_size - int(68 * ui_scaling_factor), self.icon_size - int(68 * ui_scaling_factor))
            )
            icon_circle_radius = self.icon_size // 2 - int(10 * ui_scaling_factor)
            icon_circle_center = (
                self.rect.x + icon_circle_radius - self.circle_margin - int(30 * ui_scaling_factor), 
                self.rect.y + icon_circle_radius - self.circle_margin - int(30 * ui_scaling_factor)
            )
            # Draw the icon's background circle.
            pygame.draw.circle(screen, self.color, icon_circle_center, icon_circle_radius)
            pygame.draw.circle(screen, constants.BLACK, icon_circle_center, icon_circle_radius, int(4 * ui_scaling_factor))
            
            # Draw the icon image.
            icon_rect = icon_scaled.get_rect(center=icon_circle_center)
            screen.blit(icon_scaled, icon_rect)
            
            # Draw the icon-specific hover overlay.
            if self.hover:
                icon_overlay = pygame.Surface((icon_circle_radius * 2, icon_circle_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(icon_overlay, (100, 100, 100, 110), (icon_circle_radius, icon_circle_radius), icon_circle_radius)
                screen.blit(icon_overlay, (icon_circle_center[0] - icon_circle_radius, icon_circle_center[1] - icon_circle_radius))
        
        # Draw centralized wrapped title text.
        words = self.upgrade.name.split()
        title_lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = game_state.FONTS["medium"].render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - int(40 * ui_scaling_factor):
                current_line.append(word)
            else:
                if current_line:
                    title_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            title_lines.append(' '.join(current_line))
        
        title_y = self.rect.y + int(40 * ui_scaling_factor) + (self.icon_size - int(94 * ui_scaling_factor)) + getattr(self, "title_offset", 0)
        for line in title_lines:
            title_surface = game_state.FONTS["medium"].render(line, True, constants.BLACK)
            title_rect = title_surface.get_rect(center=(self.rect.centerx, title_y))
            screen.blit(title_surface, title_rect)
            title_y += title_surface.get_height()
        
        # Render rarity text below the title.
        rarity_surface = game_state.FONTS["smaller"].render(self.upgrade.Rarity, True, constants.BLACK)
        rarity_rect = rarity_surface.get_rect(center=(self.rect.centerx, title_y - int(4 * ui_scaling_factor)))
        screen.blit(rarity_surface, rarity_rect)
        
        # Render centralized wrapped description text below rarity.
        desc_words = self.upgrade.description.split()
        desc_lines = []
        current_desc_line = []
        for word in desc_words:
            test_line = ' '.join(current_desc_line + [word])
            test_surface = game_state.FONTS["small"].render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - int(40 * ui_scaling_factor):
                current_desc_line.append(word)
            else:
                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))
                current_desc_line = [word]
        if current_desc_line:
            desc_lines.append(' '.join(current_desc_line))
        
        y_offset = rarity_rect.bottom + int(36 * ui_scaling_factor)
        for line in desc_lines:
            desc_surface = game_state.FONTS["small"].render(line, True, constants.BLACK)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(desc_surface, desc_rect)
            y_offset += desc_surface.get_height()
        
        # --- Composite Hover Overlay for the Entire Button ---
        if self.hover:
            # Create an overlay for the whole button.
            overall_overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overall_overlay.fill((100, 100, 100, 110))  # Overall hover color.
            # If an icon is present, subtract its area so it doesn’t double-darken.
            if icon_circle_center and icon_circle_radius:
                # Compute icon center relative to the button's top-left.
                rel_icon_x = icon_circle_center[0] - self.rect.x
                rel_icon_y = icon_circle_center[1] - self.rect.y
                pygame.draw.circle(overall_overlay, (0, 0, 0, 0), (rel_icon_x, rel_icon_y), icon_circle_radius)
            screen.blit(overall_overlay, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            design_mouse_pos = pygame.mouse.get_pos()
            self.hover = self.rect.collidepoint(design_mouse_pos)
        if self.cooldown > 0:  # Check if the button is on cooldown
            return False  # Ignore events if on cooldown
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Convert screen coordinates to design coordinates.
            design_mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(design_mouse_pos):
                self.cooldown = 30  # Set cooldown (e.g., 30 frames)
                return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1  # Decrease cooldown each frame
    

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
        self.skin_id: Optional[str] = None  # Use skin_id instead of skin_index.
        self.pulse_phase = 0   # For the pulsing (scaling) effect.
        self.particles = []    # List to hold particle effects.
        self.title_offset = -10 * ui_scaling_factor

    def trigger_glow(self):
        # Reset the glow timer and pulse phase for a fade-in and pulse effect.
        self.glow_timer = 0
        self.pulse_phase = 0

    def draw(self, screen):
        # Determine if this skin is currently selected by comparing IDs.
        selected = (hasattr(self, 'skin_id') and game_state.player.current_skin_id == self.skin_id)
        
        # Base settings for the glow effect
        base_glow_padding = 18 * ui_scaling_factor      # Padding around the button for the glow.
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
                    self.rect.centerx + random.uniform(-self.rect.width / 2, self.rect.width / 2),
                    self.rect.centery + random.uniform(-self.rect.height / 2, self.rect.height / 2)
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
            design_mouse_pos = pygame.mouse.get_pos()
            self.hover = self.rect.collidepoint(design_mouse_pos)
        return super().handle_event(event)
    
    