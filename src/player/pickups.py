import random
import pygame

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
        self.radius = random.randint(5, 8)
        self.lifetime = random.randint(30, 50)
        self.color = generate_shades(base_color)  # Assign a dynamically generated shade

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.1)

    def draw(self, screen):
        if self.lifetime > 0 and self.radius > 0:
            diameter = int(self.radius * 8)
            particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surf, (self.pos[0] - self.radius, self.pos[1] - self.radius))

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
