import math
from abc import ABC, abstractmethod
# from src.projectiles import BasicEnemyHomingBullet, BaseBullet, Alignment, TankEnemyBullet, BasicEnemyBullet, SniperEnemyBullet
import src.engine.constants as constants
# import src.game_state as game_state
from src.engine.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor()
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
        
        self.current_tick = 0
        self.death_animation_duration = 0.2 # seconds
        
        self.dying = False
        self.death_animation_start_tick = 0
        self.active = True
        
        self._health = self.max_health

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

    # UPDATED ABSTRACT METHOD: We now expect a single tuple `target` = (target_x, target_y)
    @abstractmethod
    def shoot(self, target_x, target_y, game_state):
        """Handle shooting logic for the enemy using in-game ticks.
        `target` is expected to be a tuple: (target_x, target_y)
        """
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
                self.death_animation_start_tick = self.current_tick
                # Reward the player only once at the start of the death animation.
                from src.engine.score import increase_score
                increase_score(self.score_reward)
                game_state.player.gain_experience(self.score_reward)

    def move(self, target_x, target_y, game_state):
        """Default movement behavior for enemies"""
        from src.engine.helpers import calculate_angle
        angle = math.radians(calculate_angle(self.x, self.y, target_x, target_y))
        self.x += self.speed * math.cos(angle) * ui_scaling_factor
        self.y += self.speed * math.sin(angle) * ui_scaling_factor
        # Restrict to screen boundaries, accounting for the experience bar
        self._restrict_to_boundaries(game_state)

    
    def update(self, target_x, target_y, game_state):
        """Default update behavior for enemies"""
        # Only perform movement and shooting if not dying.
        self.current_tick += 1
        if not self.dying:
            self.move(target_x, target_y, game_state)
            self.shoot(target_x, target_y, game_state)
            
    def _restrict_to_boundaries(self, game_state):
        """Helper method to keep enemies within screen boundaries"""
        self.x = max(20, min(self.x, game_state.screen_width - self.inner_size // 2))
        self.y = max(20, min(self.y, game_state.screen_height - self.inner_size // 2 - constants.experience_bar_height))
    
    def draw(self):
        import pygame
        import src.engine.game_state as game_state
        import src.engine.constants as constants
        from src.ui.drawing import draw_health_bar
        
        screen = game_state.screen

        # Determine alpha and death progress if dying
        alpha = 255
        if self.dying:
            death_duration_ticks = self.death_animation_duration * constants.FPS
            death_progress = (self.current_tick - self.death_animation_start_tick) / death_duration_ticks
            alpha = int(255 * (1 - death_progress))
            alpha = max(0, min(255, alpha))
            # Compute a scale factor that decreases from 1 to 0
            scale_factor = max(0, 1 - death_progress)
            # Compute new sizes for the enemy surfaces
            new_outline_size = max(1, int(self.outline_size * scale_factor))
            new_inner_size = max(1, int(self.inner_size * scale_factor))
        else:
            new_outline_size = self.outline_size
            new_inner_size = self.inner_size

        # Create surfaces with current sizes
        outline_surface = pygame.Surface((new_outline_size, new_outline_size), pygame.SRCALPHA)
        inner_surface = pygame.Surface((new_inner_size, new_inner_size), pygame.SRCALPHA)

        # Prepare colors with current alpha
        outline_color = self.outline_color
        if isinstance(outline_color, (list, tuple)) and len(outline_color) == 3:
            outline_color = (*outline_color, alpha)
        outline_surface.fill(outline_color)

        inner_color = self.inner_color
        if isinstance(inner_color, (list, tuple)) and len(inner_color) == 3:
            inner_color = (*inner_color, alpha)
        inner_surface.fill(inner_color)

        # Calculate positions
        outline_pos = (self.x - new_outline_size // 2, self.y - new_outline_size // 2)
        inner_pos = (self.x - new_inner_size // 2, self.y - new_inner_size // 2)

        # Blit the surfaces to the main screen.
        screen.blit(outline_surface, outline_pos)
        screen.blit(inner_surface, inner_pos)

        # Draw the health bar only if the enemy is still alive.
        if not self.dying:
            health_bar_x = self.x - self.inner_size // 2
            health_bar_y = self.y - self.inner_size // 2 - 12
            draw_health_bar(
                health_bar_x,
                health_bar_y,
                self.health,
                self.max_health,
                constants.TRANSLUCENT_RED,
                bar_width=self.inner_size,
                bar_height=5
            )
            
    def reset(self, x, y, scaling):
        """
        Reset common enemy properties for object pooling.
        This method reinitializes the enemy's position, scaling, health, tick counter,
        and resets state flags.
        """
        self.x = x
        self.y = y
        self.scaling = scaling
        self.current_tick = 0
        self.dying = False
        self.death_animation_start_tick = 0
        self._health = self.max_health
        self.active = True  # Mark enemy as active again
