import random
import math
from src.enemies.base import BaseEnemy
from src.projectiles import TankEnemyBullet
import src.constants as constants
import src.game_state as game_state
from src.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor()
class TankEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_tank_xp_reward * self.scaling)
        self.speed = constants.tank_speed * ui_scaling_factor
        self.outline_size = constants.TANK_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.TANK_ENEMY_INNER_SIZE
        self.outline_color = constants.TANK_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.TANK_ENEMY_INNER_COLOR
        self.initial_delay_ticks = random.uniform(1.0, constants.tank_shotgun_interval) * constants.FPS
        self.last_shotgun_tick = self.current_tick - constants.tank_shotgun_interval * constants.FPS + self.initial_delay_ticks
        
    @property
    def type(self):
        return "tank"
        
    @property
    def base_health(self):
        return constants.base_tank_health

    def shoot(self, target_x, target_y, game_state):
        if self.current_tick - self.last_shotgun_tick >= constants.tank_shotgun_interval * constants.FPS:
            from src.helpers import calculate_angle
            base_angle = calculate_angle(self.x, self.y, target_x, target_y)
            for _ in range(constants.tank_shotgun_bullet_count):
                angle = base_angle + random.uniform(-constants.tank_shotgun_spread, 
                                                    constants.tank_shotgun_spread)
                speed = random.uniform(*constants.tank_bullet_speed_range) * ui_scaling_factor
                # Use the bullet pool to get (or create) a tank bullet:
                game_state.bullet_pool.get_bullet(
                    TankEnemyBullet,
                    x=self.x,
                    y=self.y,
                    angle=angle,
                    speed=speed,
                )
            self.last_shotgun_tick = self.current_tick
