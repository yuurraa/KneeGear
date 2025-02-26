import random
import pygame
from src.engine.helpers import get_ui_scaling_factor, generate_shades

ui_scaling_factor = get_ui_scaling_factor()

class Particle:
    def __init__(self, pos, base_color):
        self.pos = list(pos)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.radius = random.randint(int(10 * ui_scaling_factor), int(16 * ui_scaling_factor))
        self.lifetime = random.randint(40, 60)
        # Generate a dynamic shade of the base color.
        self.color = generate_shades(base_color)

    def update(self):
        # Move the particle.
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        # Decrease lifetime.
        self.lifetime -= 1
        # Gradually shrink the particle.
        self.radius = max(0, self.radius - 0.1)

    def _blur_surface(self, surface, scale_factor=0.25):
        """Blur a surface by downscaling and then upscaling it."""
        width, height = surface.get_size()
        # Downscale
        small_surface = pygame.transform.smoothscale(surface, (int(width * scale_factor), int(height * scale_factor)))
        # Upscale back to original size
        blurred_surface = pygame.transform.smoothscale(small_surface, (width, height))
        return blurred_surface

    def draw(self, screen):
        if self.lifetime > 0 and self.radius > 0:
            # Draw the main particle.
            diameter = int(self.radius * 8)
            particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))
            
            # Draw the bloom (glow) effect.
            # Use a larger radius for the glow.
            glow_radius = self.radius * 1
            diameter_glow = int(glow_radius * 1)
            glow_surf = pygame.Surface((diameter_glow, diameter_glow), pygame.SRCALPHA)
            # Append an alpha value to the color for transparency (e.g., 50 out of 255).
            glow_color = self.color + (50,)
            pygame.draw.circle(glow_surf, glow_color, (int(glow_radius), int(glow_radius)), int(glow_radius))
            # Apply a simple blur to the glow.
            blurred_glow = self._blur_surface(glow_surf, scale_factor=0.25)
            # Composite the glow on top of the main screen with additive blending.
            screen.blit(blurred_glow, (self.pos[0] - glow_radius, self.pos[1] - glow_radius), special_flags=pygame.BLEND_ADD)
