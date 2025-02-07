from src.enemies.base import BaseEnemy
from src.projectiles import BasicEnemyHomingBullet, BasicEnemyBullet
import src.constants as constants
from src.helpers import calculate_angle
import math
import random
import src.game_state as game_state

from src.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor()
class BasicEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        
        # Randomized initial delay for the homing shot:
        self.initial_delay_homing_ticks = random.uniform(1.0, constants.basic_enemy_homing_interval) * constants.FPS
        self.last_shot_tick = self.current_tick - constants.basic_enemy_homing_interval * constants.FPS + self.initial_delay_homing_ticks
        
        # Randomized initial delay for the AOE shot:
        self.initial_delay_aoe_ticks = random.uniform(1.0, constants.basic_enemy_bullet_interval) * constants.FPS
        self.last_aoe_tick = self.current_tick - constants.basic_enemy_bullet_interval * constants.FPS + self.initial_delay_aoe_ticks
        
        self.score_reward = math.floor(constants.base_basic_enemy_xp_reward * self.scaling)
        self.speed = constants.basic_enemy_speed * ui_scaling_factor
        self.outline_size = constants.REGULAR_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.REGULAR_ENEMY_INNER_SIZE
        self.outline_color = constants.REGULAR_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.REGULAR_ENEMY_INNER_COLOR

    @property
    def type(self):
        return "basic"
        
    @property
    def base_health(self):
        return constants.base_basic_enemy_health

    def shoot(self, target_x, target_y, game_state):
        # Convert ticks to seconds
        current_time = self.current_tick / constants.FPS
        last_shot_time = self.last_shot_tick / constants.FPS
        last_aoe_time = self.last_aoe_tick / constants.FPS

        # Homing shot using seconds
        if current_time - last_shot_time >= constants.basic_enemy_homing_interval:
            angle = calculate_angle(self.x, self.y, target_x, target_y)
            bullet = BasicEnemyHomingBullet(
                x=self.x,
                y=self.y,
                angle=angle,
            )
            game_state.projectiles.append(bullet)
            self.last_shot_tick = self.current_tick

        # AOE shot using seconds
        if current_time - last_aoe_time >= constants.basic_enemy_bullet_interval:
            for angle in range(0, 360, 45):
                bullet = BasicEnemyBullet(
                    x=self.x,
                    y=self.y,
                    angle=angle,
                )
                game_state.projectiles.append(bullet)
            self.last_aoe_tick = self.current_tick
