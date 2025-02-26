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