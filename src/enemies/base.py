import math
from abc import ABC, abstractmethod

import random

from src.projectiles import BasicEnemyHomingBullet, BaseBullet, Alignment, TankEnemyBullet, BasicEnemyBullet, SniperEnemyBullet
import src.constants as constants
class BaseEnemy(ABC):
    def __init__(self, x, y, scaling):
        self.x = x
        self.y = y
        self.scaling = scaling
        self.score_reward = 5
        self.speed = 0
        
        self.outline_size = 0
        self.inner_size = 0
        self.outline_color = 0
        self.inner_color = 0
        
        self.dying = False
        self.death_timer = 30  # Timer for death animation (in ticks)
        
    @property
    @abstractmethod
    def type(self):
        pass
        
    @property
    @abstractmethod
    def base_health(self):
        pass
        
    @property
    def max_health(self):
        return math.floor(self.base_health * self.scaling)
        
    @property
    def health(self):
        return self._health
        
    @health.setter
    def health(self, value):
        self._health = value

    @abstractmethod
    def shoot(self, target_x, target_y, current_tick, game_state):
        """Handle shooting logic for the enemy using in-game ticks"""
        pass
        
    def apply_damage(self, damage, game_state):
        """Apply damage to the enemy and handle related effects."""
        self._health -= damage

        # Add damage number (existing code)
        game_state.damage_numbers.append({
            "x": self.x,
            "y": self.y,
            "value": damage,
            "timer": 20,
            "color": constants.PURPLE
        })

        if self._health <= 0:
            if not self.dying:
                # Mark enemy as dying and set a death animation timer (say 60 ticks)
                self.dying = True
                self.death_timer = 60
                # Reward the player only once at the start of the death animation.
                from src.score import increase_score
                increase_score(self.score_reward)
                game_state.player.gain_experience(self.score_reward)
            # Return True if the enemy is dead or dying (so that damage numbers might be processed)
            return True
        return False

    def move(self, target_x, target_y, game_state):
        """Default movement behavior for enemies"""
        from src.helpers import calculate_angle
        angle = math.radians(calculate_angle(self.x, self.y, target_x, target_y))
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        # Restrict to screen boundaries, accounting for the experience bar
        self._restrict_to_boundaries(game_state)
    

    def update(self, target_x, target_y, current_tick, game_state):
        """Default update behavior for enemies"""
        if self.dying:
            return
        self.move(target_x, target_y, game_state)
        self.shoot(target_x, target_y, current_tick, game_state)
    
        
    def _restrict_to_boundaries(self, game_state):
        """Helper method to keep enemies within screen boundaries"""
        self.x = max(20, min(self.x, game_state.screen_width - 20))
        self.y = max(20, min(self.y, game_state.screen_height - 20 - constants.experience_bar_height))
    
    def draw(self):
        import pygame
        import src.game_state as game_state
        import src.constants as constants
        from src.drawing import draw_health_bar
        
        def dissolve_surface(surface, death_progress):
            """
            Returns a new surface where a fraction of the pixels (determined by death_progress)
            have been set fully transparent. death_progress should be between 0 (no dissolve)
            and 1 (fully dissolved).
            """
            # Create a copy with per-pixel alpha
            new_surface = surface.copy()
            new_surface = new_surface.convert_alpha()  # Ensure alpha channel

            width, height = new_surface.get_size()
            for x in range(width):
                for y in range(height):
                    # For each pixel, with probability equal to death_progress, clear it.
                    if random.random() < death_progress:
                        # Set pixel fully transparent.
                        new_surface.set_at((x, y), (0, 0, 0, 0))
            return new_surface

        screen = game_state.screen

        # Determine alpha and death progress if dying.
        # Assume the death animation lasts for 60 ticks.
        max_death_timer = 60
        alpha = 255
        death_progress = 0.0  # 0 means no dissolve; 1 means fully dissolved.
        if self.dying:
            death_progress = (max_death_timer - self.death_timer) / max_death_timer
            alpha = int(255 * (1 - death_progress))
            alpha = max(0, min(255, alpha))

        # Create surfaces for drawing the enemy shapes with per-pixel alpha.
        outline_surface = pygame.Surface((self.outline_size, self.outline_size), pygame.SRCALPHA)
        inner_surface = pygame.Surface((self.inner_size, self.inner_size), pygame.SRCALPHA)

        # Prepare the outline color with current alpha.
        outline_color = self.outline_color
        if isinstance(outline_color, (list, tuple)) and len(outline_color) == 3:
            outline_color = (*outline_color, alpha)
        # Fill the outline surface with the outline color.
        outline_surface.fill(outline_color)

        # Prepare the inner color with current alpha.
        inner_color = self.inner_color
        if isinstance(inner_color, (list, tuple)) and len(inner_color) == 3:
            inner_color = (*inner_color, alpha)
        inner_surface.fill(inner_color)

        # If the enemy is dying, apply the dissolve effect.
        if self.dying:
            outline_surface = dissolve_surface(outline_surface, death_progress)
            inner_surface = dissolve_surface(inner_surface, death_progress)

        # Blit the surfaces to the main screen.
        screen.blit(outline_surface, (self.x - self.outline_size // 2, self.y - self.outline_size // 2))
        screen.blit(inner_surface, (self.x - self.inner_size // 2, self.y - self.inner_size // 2))

        # Draw the health bar only if the enemy is still alive.
        # If dying, fade it out and also apply a dissolve effect.
        if not self.dying:
            health_bar_x = self.x - self.inner_size // 2
            health_bar_y = self.y - 35
            draw_health_bar(
                health_bar_x,
                health_bar_y,
                self.health,
                self.max_health,
                constants.TRANSLUCENT_RED,
                bar_width=self.inner_size,
                bar_height=5
            )
        else:
            # Create a temporary surface for the health bar.
            health_bar_width = self.inner_size
            health_bar_height = 5
            health_bar_surface = pygame.Surface((health_bar_width, health_bar_height), pygame.SRCALPHA)
            # Fade out the health bar color.
            bar_color = list(constants.TRANSLUCENT_RED)
            bar_color[-1] = alpha  # adjust alpha
            health_bar_surface.fill(tuple(bar_color))
            # Optionally, apply the dissolve effect.
            health_bar_surface = dissolve_surface(health_bar_surface, death_progress)
            screen.blit(health_bar_surface, (self.x - health_bar_width // 2, self.y - 35))
