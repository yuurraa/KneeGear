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
        self.initial_delay_ticks = random.uniform(2.0, constants.sniper_volley_interval) * constants.FPS
        self.last_shot_tick = game_state.in_game_ticks_elapsed - constants.sniper_volley_interval * constants.FPS + self.initial_delay_ticks
        self.last_volley_shot_tick = self.last_shot_tick
        self.shots_fired_in_volley = 69
        
        self.speed = constants.sniper_move_speed
        self.outline_size = constants.SNIPER_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.SNIPER_ENEMY_INNER_SIZE
        self.outline_color = constants.SNIPER_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.SNIPER_ENEMY_INNER_COLOR
        
        self.strafe_timer = 0
        self.current_strafe_angle = random.uniform(0, 2 * math.pi)

    @property
    def type(self):
        return "sniper"
    
    @property
    def base_health(self):
        return constants.base_sniper_health


    def move(self, target_x, target_y, game_state):
        # Calculate vector from player to sniper (player position is target_x, target_y)
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        # Normalize the vector (direction from sniper to player)
        if distance != 0:
            norm_dx = dx / distance
            norm_dy = dy / distance
        else:
            norm_dx, norm_dy = 0, 0

        base_speed = self.speed  # Base movement speed
        move_x, move_y = 0, 0    # Initialize movement deltas

        # 1. If the player is too close, retreat directly (with increased speed):
        if distance < constants.sniper_keep_distance:
            retreat_angle = math.atan2(self.y - target_y, self.x - target_x)
            move_x = math.cos(retreat_angle) * base_speed * constants.sniper_retreat_multiplier
            move_y = math.sin(retreat_angle) * base_speed * constants.sniper_retreat_multiplier
            self.strafe_timer = 0  # Reset strafe timer

        # 2. If the player is too far, approach the player:
        elif distance > constants.sniper_approach_distance:
            approach_angle = math.atan2(dy, dx)
            move_x = math.cos(approach_angle) * base_speed
            move_y = math.sin(approach_angle) * base_speed
            self.strafe_timer = 0  # Reset strafe timer

        # 3. Otherwise (player is within the ideal range), strafe:
        else:
            if self.strafe_timer <= 0:
                self.current_strafe_angle = random.uniform(0, 2 * math.pi)
                self.strafe_timer = constants.sniper_strafe_duration
            move_x = math.cos(self.current_strafe_angle) * base_speed
            move_y = math.sin(self.current_strafe_angle) * base_speed
            self.strafe_timer -= 1

            # Add a small component to gradually increase the distance from the player.
            move_x += -norm_dx * constants.sniper_strafe_retreat_factor
            move_y += -norm_dy * constants.sniper_strafe_retreat_factor

        # --- Boundary-Aware Adjustment ---
        # We assume the game boundaries are from 0 to game_state.screen_width (x)
        # and 0 to game_state.screen_height (y). Adjust if your boundaries differ.
        blocked_x = False
        blocked_y = False

        # Check horizontal boundaries.
        if self.x <= 0 and move_x < 0:
            blocked_x = True
            move_x = 0
        elif self.x >= game_state.screen_width and move_x > 0:
            blocked_x = True
            move_x = 0

        # Check vertical boundaries.
        if self.y <= 0 and move_y < 0:
            blocked_y = True
            move_y = 0
        elif self.y >= game_state.screen_height and move_y > 0:
            blocked_y = True
            move_y = 0

        # If one axis is blocked, try to slide along the wall instead of stopping completely.
        # (Only apply if the movement in that axis is near zero.)
        if blocked_x and abs(move_x) < 0.001:
            # When horizontal movement is blocked, choose vertical movement away from the player.
            # For example, if the player is above, slide downward; if below, slide upward.
            if target_y < self.y:
                move_y = base_speed  # move downward
            else:
                move_y = -base_speed  # move upward

        if blocked_y and abs(move_y) < 0.001:
            # When vertical movement is blocked, choose horizontal movement away from the player.
            if target_x < self.x:
                move_x = base_speed  # move right
            else:
                move_x = -base_speed  # move left

        # Fallback in case both axes ended up blocked (e.g. in a corner)
        if abs(move_x) < 0.001 and abs(move_y) < 0.001:
            # Use a fallback direction away from the player.
            fallback_angle = math.atan2(self.y - target_y, self.x - target_x)
            move_x = math.cos(fallback_angle) * base_speed * constants.sniper_retreat_multiplier
            move_y = math.sin(fallback_angle) * base_speed * constants.sniper_retreat_multiplier

        # Update sniper position
        self.x += move_x
        self.y += move_y

        # Finally, ensure the sniper remains within screen boundaries.
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
            
            # Add a small random spread to the aim angle.
            # Ensure you define constants.sniper_bullet_spread in your constants file, e.g. 0.0873 for ±5°.
            spread = constants.sniper_bullet_spread  
            angle_offset = random.uniform(-spread, spread)
            aim_angle += angle_offset
            
            bullet = SniperEnemyBullet(
                x=self.x,
                y=self.y,
                angle=aim_angle,
                speed=constants.sniper_bullet_speed,
            )
            game_state.projectiles.append(bullet)
            
            self.shots_fired_in_volley += 1
            self.last_volley_shot_tick = current_tick

