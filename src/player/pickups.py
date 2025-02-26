import random
import pygame
from src.engine.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor()

def generate_shades(base_color, variation=30):
    """Generate a random shade of the given base color with slight variation."""
    r, g, b = base_color
    return (
        max(0, min(255, r + random.randint(-variation, variation))),
        max(0, min(255, g + random.randint(-variation, variation))),
        max(0, min(255, b + random.randint(-variation, variation)))
    )

class HeartParticle:
    def __init__(self, pos, base_color):
        self.pos = list(pos)
        self.velocity = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
        self.radius = random.randint(int(10 * ui_scaling_factor), int(16 * ui_scaling_factor))
        self.lifetime = random.randint(30, 50)
        self.color = generate_shades(base_color)  # Dynamically generated shade

    def update(self):
        import src.engine.game_state as game_state
        from src.player.player import PlayerState
        if (not game_state.paused and not game_state.game_over and 
            not game_state.showing_upgrades and not game_state.showing_stats and 
            game_state.player.state != PlayerState.LEVELING_UP):
            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]
            self.lifetime -= 1
            self.radius = max(0, self.radius - 0.1)

    def _blur_surface(self, surface, scale_factor=0.25):
        """Blurs a surface by downscaling then upscaling it."""
        width, height = surface.get_size()
        small_surface = pygame.transform.smoothscale(surface, (int(width * scale_factor), int(height * scale_factor)))
        blurred_surface = pygame.transform.smoothscale(small_surface, (width, height))
        return blurred_surface

    def draw(self, screen):
        if self.lifetime > 0 and self.radius > 0:
            # --- Draw the main particle ---
            diameter = int(self.radius * 2)
            particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))
            
            # --- Draw the bloom (glow) effect ---
            # Use a larger radius for the bloom
            glow_radius = self.radius * 1
            diameter_glow = int(glow_radius * 1)
            glow_surf = pygame.Surface((diameter_glow, diameter_glow), pygame.SRCALPHA)
            # Append an alpha value to create a semi-transparent glow
            glow_color = self.color + (50,)  # 50 is a low alpha for subtle glow
            pygame.draw.circle(glow_surf, glow_color, (int(glow_radius), int(glow_radius)), int(glow_radius))
            # Apply the blur to the glow surface
            blurred_glow = self._blur_surface(glow_surf, scale_factor=0.25)
            # Use additive blending to composite the bloom over the particle
            screen.blit(blurred_glow, (self.pos[0] - glow_radius, self.pos[1] - glow_radius), special_flags=pygame.BLEND_ADD)

class HeartEffect:
    def __init__(self, pos, base_color, particle_count=25):
        self.pos = pos
        self.base_color = base_color
        self.particles = [HeartParticle(pos, base_color) for _ in range(particle_count)]
    
    def update(self):
        for particle in self.particles:
            particle.update()
        # Replace dead particles
        for i, particle in enumerate(self.particles):
            if particle.lifetime <= 0 or particle.radius <= 0:
                self.particles[i] = HeartParticle(self.pos, self.base_color)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
