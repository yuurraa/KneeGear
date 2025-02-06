import random
import math
from src.enemies.base import BaseEnemy
from src.projectiles import TankEnemyBullet
import src.constants as constants
import src.game_state as game_state

class TankEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health  # Already correctly set through property
        self.score_reward = math.floor(constants.base_tank_xp_reward * self.scaling)

        # Ensure speed is scaled only once
        self.speed = constants.tank_speed * game_state.scale 

        # Sizes (scaled once)
        self.outline_size = constants.TANK_ENEMY_OUTLINE_SIZE * game_state.scale
        self.inner_size = constants.TANK_ENEMY_INNER_SIZE * game_state.scale

        self.outline_color = constants.TANK_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.TANK_ENEMY_INNER_COLOR

        # Initial delay (ensure not scaled twice)
        self.initial_delay_ticks = random.uniform(1.0, constants.tank_shotgun_interval) * constants.FPS
        self.last_shotgun_tick = self.current_tick - (constants.tank_shotgun_interval * constants.FPS) + self.initial_delay_ticks

    @property
    def type(self):
        return "tank"
        
    @property
    def base_health(self):
        return constants.base_tank_health * game_state.scale  # Ensure health is scaled only once

    def shoot(self, target_x, target_y, game_state):
        # Check if enough time has passed to shoot
        if self.current_tick - self.last_shotgun_tick >= constants.tank_shotgun_interval * constants.FPS:
            from src.helpers import calculate_angle

            base_angle = calculate_angle(self.x, self.y, target_x, target_y)
            
            for _ in range(constants.tank_shotgun_pellet_count):
                # Spread should be scaled if it's in world units
                spread = constants.tank_shotgun_spread * game_state.scale
                angle = base_angle + random.uniform(-spread, spread)

                # Speed should only be scaled if it's not already scaled elsewhere
                pellet_speed = random.uniform(*constants.tank_pellet_speed_range) * game_state.scale 

                pellet = TankEnemyBullet(
                    x=self.x,
                    y=self.y,
                    angle=angle,
                    speed=pellet_speed,  
                )
                game_state.projectiles.append(pellet)

            self.last_shotgun_tick = self.current_tick
