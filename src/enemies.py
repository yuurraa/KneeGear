import math
import constants
from abc import ABC, abstractmethod
from projectiles import BasicEnemyHomingBullet, BaseBullet, Alignment, TankEnemyBullet, BasicEnemyBullet
import random

class Enemy(ABC):
    def __init__(self, x, y, scaling):
        self.x = x
        self.y = y
        self.scaling = scaling
        self.last_shot_time = 0
        self.last_aoe_time = 0
        self.score_reward = 5
        
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
    def shoot(self, target_x, target_y, current_time, game_state):
        """Handle shooting logic for the enemy"""
        pass
        
class RegularEnemy(Enemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_basic_enemy_xp_reward * self.scaling)
        
    @property
    def type(self):
        return "regular"
        
    @property
    def base_health(self):
        return constants.base_basic_enemy_health

    def shoot(self, target_x, target_y, current_time, game_state):
        # Homing shot
        if current_time - self.last_shot_time >= constants.basic_enemy_homing_interval:
            from helpers import calculate_angle
            angle = calculate_angle(self.x, self.y, target_x, target_y)
            bullet = BasicEnemyHomingBullet(
                x=self.x,
                y=self.y,
                angle=angle,
            )
            game_state.projectiles.append(bullet)
            self.last_shot_time = current_time

        # AOE shot
        if current_time - self.last_aoe_time >= constants.basic_enemy_bullet_interval:
            for angle in range(0, 360, 45):
                bullet = BasicEnemyBullet(
                    x=self.x,
                    y=self.y,
                    angle=angle,
                )
                game_state.projectiles.append(bullet)
            self.last_aoe_time = current_time

class TankEnemy(Enemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_tank_xp_reward * self.scaling)
        self.last_shotgun_time = 0
        
    @property
    def type(self):
        return "tank"
        
    @property
    def base_health(self):
        return constants.base_tank_health

    def shoot(self, target_x, target_y, current_time, game_state):
        if current_time - self.last_shotgun_time >= constants.tank_shotgun_interval:
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
            self.last_shotgun_time = current_time
        