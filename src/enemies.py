import math
import constants
from abc import ABC, abstractmethod
from projectiles import BasicEnemyHomingBullet, BaseBullet, Alignment, TankEnemyBullet, BasicEnemyBullet, SniperEnemyBullet
import random

class Enemy(ABC):
    def __init__(self, x, y, scaling):
        self.x = x
        self.y = y
        self.scaling = scaling
        self.last_shot_tick = 0      # Using in-game tick counter for shooting events
        self.last_aoe_tick = 0       # Using in-game tick counter for AOE events
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
            from score import increase_score
            increase_score(self.score_reward)
            game_state.player.gain_experience(self.score_reward)
            return True
        return False

    def move(self, target_x, target_y, game_state):
        """Default movement behavior for enemies"""
        from helpers import calculate_angle
        angle = math.radians(calculate_angle(self.x, self.y, target_x, target_y))
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        # Restrict to screen boundaries, accounting for the experience bar
        self._restrict_to_boundaries(game_state)
        
    def _restrict_to_boundaries(self, game_state):
        """Helper method to keep enemies within screen boundaries"""
        self.x = max(20, min(self.x, game_state.screen_width - 20))
        self.y = max(20, min(self.y, game_state.screen_height - 20 - constants.experience_bar_height))
    
    def draw(self):
        import pygame
        import game_state
        import constants
        from drawing import draw_health_bar  # re-use the helper from drawing.py

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


class RegularEnemy(Enemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_basic_enemy_xp_reward * self.scaling)
        self.speed = constants.basic_enemy_speed
        self.outline_size = constants.REGULAR_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.REGULAR_ENEMY_INNER_SIZE
        self.outline_color = constants.REGULAR_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.REGULAR_ENEMY_INNER_COLOR
        

    @property
    def type(self):
        return "regular"
        
    @property
    def base_health(self):
        return constants.base_basic_enemy_health

    def shoot(self, target_x, target_y, current_tick, game_state):
        # Convert ticks to seconds
        current_time = current_tick / constants.FPS
        last_shot_time = self.last_shot_tick / constants.FPS
        last_aoe_time = self.last_aoe_tick / constants.FPS

        # Homing shot using seconds
        if current_time - last_shot_time >= constants.basic_enemy_homing_interval:
            from helpers import calculate_angle
            angle = calculate_angle(self.x, self.y, target_x, target_y)
            bullet = BasicEnemyHomingBullet(
                x=self.x,
                y=self.y,
                angle=angle,
            )
            game_state.projectiles.append(bullet)
            self.last_shot_tick = current_tick

        # AOE shot using seconds
        if current_time - last_aoe_time >= constants.basic_enemy_bullet_interval:
            for angle in range(0, 360, 45):
                bullet = BasicEnemyBullet(
                    x=self.x,
                    y=self.y,
                    angle=angle,
                )
                game_state.projectiles.append(bullet)
            self.last_aoe_tick = current_tick



class TankEnemy(Enemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_tank_xp_reward * self.scaling)
        self.speed = constants.tank_speed
        self.outline_size = constants.TANK_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.TANK_ENEMY_INNER_SIZE
        self.outline_color = constants.TANK_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.TANK_ENEMY_INNER_COLOR
        self.last_shotgun_tick = 0  # Using in-game tick counter for shotgun timing
        
    @property
    def type(self):
        return "tank"
        
    @property
    def base_health(self):
        return constants.base_tank_health

    def shoot(self, target_x, target_y, current_tick, game_state):
        # Convert ticks to seconds
        current_time = current_tick / constants.FPS
        last_shotgun_time = self.last_shotgun_tick / constants.FPS

        if current_time - last_shotgun_time >= constants.tank_shotgun_interval:
            from helpers import calculate_angle
            base_angle = calculate_angle(self.x, self.y, target_x, target_y)
            for _ in range(constants.tank_shotgun_pellet_count):
                angle = base_angle + random.uniform(-constants.tank_shotgun_spread, 
                                                      constants.tank_shotgun_spread)
                speed = random.uniform(*constants.tank_pellet_speed_range)
                pellet = TankEnemyBullet(
                    x=self.x,
                    y=self.y,
                    angle=angle,
                    speed=speed,
                )
                game_state.projectiles.append(pellet)
            self.last_shotgun_tick = current_tick
        

class SniperEnemy(Enemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        import game_state
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_sniper_xp_reward * self.scaling)
        self.last_volley_shot_tick = 0  
        self.shots_fired_in_volley = 69  # Track number of shots in current volley
        self.speed = constants.sniper_move_speed
        self.outline_size = constants.SNIPER_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.SNIPER_ENEMY_INNER_SIZE
        self.outline_color = constants.SNIPER_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.SNIPER_ENEMY_INNER_COLOR
        

    @property
    def type(self):
        return "sniper"
    
    @property
    def base_health(self):
        return constants.base_sniper_health

    def move(self, target_x, target_y, game_state):
        # Sniper keeps its custom movement behavior
        # Retreat if too close to the player
        dx = self.x - target_x
        dy = self.y - target_y
        distance = math.hypot(dx, dy)
        
        if distance < constants.sniper_keep_distance:
            # Move away from the player
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
        else:
            # Use default movement behavior to approach the player
            super().move(target_x, target_y, game_state)
            
        # Restrict to screen boundaries
        self._restrict_to_boundaries(game_state)

    def shoot(self, target_x, target_y, current_tick, game_state):
        # Convert ticks to seconds
        current_time = current_tick / constants.FPS
        last_shot_time = self.last_shot_tick / constants.FPS
        last_volley_shot_time = self.last_volley_shot_tick / constants.FPS

        if current_time - last_shot_time >= constants.sniper_volley_interval:
            self.shots_fired_in_volley = 0
            self.last_volley_shot_tick = current_tick
            self.last_shot_tick = current_tick

        if (self.shots_fired_in_volley < 3 and 
            current_time - last_volley_shot_time >= constants.sniper_shot_delay):
            from helpers import calculate_angle
            aim_angle = calculate_angle(self.x, self.y, target_x, target_y)
            
            bullet = SniperEnemyBullet(
                x=self.x,
                y=self.y,
                angle=aim_angle,
                speed=constants.sniper_bullet_speed,
            )
            game_state.projectiles.append(bullet)
            
            self.shots_fired_in_volley += 1
            self.last_volley_shot_tick = current_tick
        