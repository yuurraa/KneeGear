import math
from abc import ABC, abstractmethod
import random

from src.projectiles import (
    BasicEnemyHomingBullet, BaseBullet, Alignment, 
    TankEnemyBullet, BasicEnemyBullet, SniperEnemyBullet
)
from src.helpers import get_scaled_font
import src.game_state as game_state
import src.constants as constants

class BaseEnemy(ABC):
    def __init__(self, x, y, scaling):
        self.x = x
        self.y = y
        self.scaling = scaling
        self.score_reward = 5

        # Scaling-based attributes
        self.speed = constants.ENEMY_BASE_SPEED * game_state.scale
        self.outline_size = constants.ENEMY_OUTLINE_SIZE * game_state.scale
        self.inner_size = constants.ENEMY_INNER_SIZE * game_state.scale

        self.outline_color = constants.ENEMY_OUTLINE_COLOR
        self.inner_color = constants.ENEMY_INNER_COLOR

        self.current_tick = 0
        self.death_animation_duration = 0.2  # seconds

        self.dying = False
        self.death_animation_start_tick = 0

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
    def shoot(self, target_x, target_y, game_state):
        """Handle shooting logic for the enemy using in-game ticks"""
        pass

    def apply_damage(self, damage, game_state):
        """Apply damage to the enemy and handle related effects."""
        self._health -= damage

        # Add scaled damage numbers
        game_state.damage_numbers.append({
            "x": self.x,
            "y": self.y,
            "value": damage,
            "timer": int(20 * game_state.scale),  # Scale the lifespan
            "color": constants.PURPLE
        })

        if self._health <= 0 and not self.dying:
            # Mark enemy as dying and start death animation
            self.dying = True
            self.death_animation_start_tick = self.current_tick

            # Reward the player
            from src.score import increase_score
            increase_score(self.score_reward)
            game_state.player.gain_experience(self.score_reward)

    def move(self, target_x, target_y, game_state):
        """Default movement behavior for enemies"""
        from src.helpers import calculate_angle
        angle = math.radians(calculate_angle(self.x, self.y, target_x, target_y))
        
        # Move using scaled speed
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        
        # Restrict position to screen boundaries
        self._restrict_to_boundaries(game_state)

    def update(self, target_x, target_y, game_state):
        """Default update behavior for enemies"""
        self.current_tick += 1

        if not self.dying:
            self.move(target_x, target_y, game_state)
            self.shoot(target_x, target_y, game_state)

        # Handle death animation timing
        if self.dying and self.current_tick - self.death_animation_start_tick > self.death_animation_duration * constants.FPS:
            game_state.enemies.remove(self)

    def _restrict_to_boundaries(self, game_state):
        """Helper method to keep enemies within screen boundaries"""
        margin = 20 * game_state.scale
        self.x = max(margin, min(self.x, game_state.screen_width - margin))
        self.y = max(margin, min(self.y, game_state.screen_height - margin - (constants.experience_bar_height * game_state.scale)))

    def draw(self):
        import pygame
        from src.drawing import draw_health_bar

        screen = game_state.screen

        # Handle death animation scaling & transparency
        alpha = 255
        if self.dying:
            death_duration_ticks = self.death_animation_duration * constants.FPS
            death_progress = (self.current_tick - self.death_animation_start_tick) / death_duration_ticks
            alpha = int(255 * (1 - death_progress))
            alpha = max(0, min(255, alpha))
            scale_factor = max(0, 1 - death_progress)

            new_outline_size = max(1, int(self.outline_size * scale_factor))
            new_inner_size = max(1, int(self.inner_size * scale_factor))
        else:
            new_outline_size = self.outline_size
            new_inner_size = self.inner_size

        # Create surfaces with scaling
        outline_surface = pygame.Surface((new_outline_size, new_outline_size), pygame.SRCALPHA)
        inner_surface = pygame.Surface((new_inner_size, new_inner_size), pygame.SRCALPHA)

        # Apply alpha transparency
        outline_color = (*self.outline_color, alpha) if isinstance(self.outline_color, (tuple, list)) else self.outline_color
        inner_color = (*self.inner_color, alpha) if isinstance(self.inner_color, (tuple, list)) else self.inner_color

        outline_surface.fill(outline_color)
        inner_surface.fill(inner_color)

        # Calculate positions for drawing
        outline_pos = (self.x - new_outline_size // 2, self.y - new_outline_size // 2)
        inner_pos = (self.x - new_inner_size // 2, self.y - new_inner_size // 2)

        # Draw enemy
        screen.blit(outline_surface, outline_pos)
        screen.blit(inner_surface, inner_pos)

        # Draw scaled health bar
        if not self.dying:
            health_bar_x = self.x - self.inner_size // 2
            health_bar_y = self.y - (35 * game_state.scale)

            draw_health_bar(
                health_bar_x,
                health_bar_y,
                self.health,
                self.max_health,
                constants.TRANSLUCENT_RED,
                bar_width=self.inner_size,
                bar_height=int(5 * game_state.scale)  # Scale the bar height
            )
