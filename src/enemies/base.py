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
        """Apply damage to the enemy and handle related effects"""
        self._health -= damage
        
        # Add damage number
        game_state.damage_numbers.append({
            "x": self.x,
            "y": self.y,
            "value": damage,
            "timer": 20,
            "color": constants.PURPLE
        })
        
        # Handle death and rewards
        if self._health <= 0:
            from src.score import increase_score
            increase_score(self.score_reward)
            game_state.player.gain_experience(self.score_reward)
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
        from src.drawing import draw_health_bar  # re-use the helper from drawing.py

        screen = game_state.screen

        # Draw the outer (outline) rectangle
        pygame.draw.rect(
            screen,
            self.outline_color,
            (self.x - self.outline_size // 2, self.y - self.outline_size // 2, self.outline_size, self.outline_size)
        )

        # Draw the inner (main) rectangle
        pygame.draw.rect(
            screen,
            self.inner_color,
            (self.x - self.inner_size // 2, self.y - self.inner_size // 2, self.inner_size, self.inner_size)
        )

        # Draw health bar above the enemy
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
