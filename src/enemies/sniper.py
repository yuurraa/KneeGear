import math
from src.enemies.base import BaseEnemy
import src.constants as constants
from src.projectiles import SniperEnemyBullet
import random
import src.game_state as game_state

class SniperEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_sniper_xp_reward * self.scaling)
        
        # Apply randomized initial delay for the volley shot
        self.initial_delay_ticks = random.uniform(1.0, constants.sniper_volley_interval) * constants.FPS
        self.last_shot_tick = game_state.in_game_ticks_elapsed - constants.sniper_volley_interval * constants.FPS + self.initial_delay_ticks
        self.last_volley_shot_tick = self.last_shot_tick
        self.shots_fired_in_volley = 0
        
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
            from src.helpers import calculate_angle
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
