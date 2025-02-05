import random
import math
from src.enemies.base import BaseEnemy
from src.projectiles import TankEnemyBullet
import src.constants as constants
import src.game_state as game_state

class TankEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_tank_xp_reward * self.scaling)
        self.speed = constants.tank_speed
        self.outline_size = constants.TANK_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.TANK_ENEMY_INNER_SIZE
        self.outline_color = constants.TANK_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.TANK_ENEMY_INNER_COLOR
        self.initial_delay_ticks = random.uniform(1.0, constants.tank_shotgun_interval) * constants.FPS
        self.last_shotgun_tick = game_state.in_game_ticks_elapsed - constants.tank_shotgun_interval * constants.FPS + self.initial_delay_ticks
        
    @property
    def type(self):
        return "tank"
        
    @property
    def base_health(self):
        return constants.base_tank_health

    def shoot(self, target_x, target_y, current_tick, game_state):
        # Convert ticks to seconds
        if current_tick - self.last_shotgun_tick >= constants.tank_shotgun_interval * constants.FPS:
            from src.helpers import calculate_angle
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
