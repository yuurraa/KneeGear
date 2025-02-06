import math
import random
from src.enemies.base import BaseEnemy
import src.constants as constants
from src.projectiles import SniperEnemyBullet
import src.game_state as game_state

class SniperEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_sniper_xp_reward * self.scaling)

        # Apply randomized initial delay for volley shot (scaled)
        self.initial_delay_ticks = random.uniform(2.0, constants.sniper_volley_interval) * constants.FPS
        self.last_shot_tick = self.current_tick - (constants.sniper_volley_interval * constants.FPS) + self.initial_delay_ticks
        self.last_volley_shot_tick = self.last_shot_tick
        self.shots_fired_in_volley = 0

        # Apply scaling to movement and size
        self.speed = constants.sniper_move_speed * game_state.scale
        self.outline_size = constants.SNIPER_ENEMY_OUTLINE_SIZE * game_state.scale
        self.inner_size = constants.SNIPER_ENEMY_INNER_SIZE * game_state.scale
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
        """Handles movement logic, including approach, retreat, and strafing."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        # Normalize movement vector
        if distance != 0:
            norm_dx = dx / distance
            norm_dy = dy / distance
        else:
            norm_dx, norm_dy = 0, 0

        base_speed = self.speed  # Scaled speed
        move_x, move_y = 0, 0  

        # 1. Retreat if too close (scaled retreat speed)
        if distance < constants.sniper_keep_distance * game_state.scale:
            retreat_angle = math.atan2(self.y - target_y, self.x - target_x)
            move_x = math.cos(retreat_angle) * base_speed * constants.sniper_retreat_multiplier
            move_y = math.sin(retreat_angle) * base_speed * constants.sniper_retreat_multiplier
            self.strafe_timer = 0  

        # 2. Approach if too far (scaled approach range)
        elif distance > constants.sniper_approach_distance * game_state.scale:
            approach_angle = math.atan2(dy, dx)
            move_x = math.cos(approach_angle) * base_speed
            move_y = math.sin(approach_angle) * base_speed
            self.strafe_timer = 0  

        # 3. Strafe if within ideal range
        else:
            if self.strafe_timer <= 0:
                self.current_strafe_angle = random.uniform(0, 2 * math.pi)
                self.strafe_timer = constants.sniper_strafe_duration
            move_x = math.cos(self.current_strafe_angle) * base_speed
            move_y = math.sin(self.current_strafe_angle) * base_speed
            self.strafe_timer -= 1

            # Add small retreat component to maintain distance
            move_x += -norm_dx * constants.sniper_strafe_retreat_factor
            move_y += -norm_dy * constants.sniper_strafe_retreat_factor
        # --- Boundary-Aware Adjustment ---
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

        # If one axis is blocked, slide along the other axis instead of stopping completely.
        if blocked_x and abs(move_x) < 0.001:
            move_y = base_speed if target_y < self.y else -base_speed
        if blocked_y and abs(move_y) < 0.001:
            move_x = base_speed if target_x < self.x else -base_speed

        # Fallback in case both axes are blocked (e.g., cornered)
        if abs(move_x) < 0.001 and abs(move_y) < 0.001:
            fallback_angle = math.atan2(self.y - target_y, self.x - target_x)
            move_x = math.cos(fallback_angle) * base_speed * constants.sniper_retreat_multiplier
            move_y = math.sin(fallback_angle) * base_speed * constants.sniper_retreat_multiplier

        # Update position
        self.x += move_x
        self.y += move_y
        
        # Apply screen boundary checks
        self.x = max(20, min(self.x + move_x, game_state.screen_width - 20))
        self.y = max(20, min(self.y + move_y, game_state.screen_height - 20 - constants.experience_bar_height))

    def shoot(self, target_x, target_y, game_state):
        """Handles shooting behavior, scaling bullet timing and spread."""
        current_time = self.current_tick / constants.FPS
        last_shot_time = self.last_shot_tick / constants.FPS
        last_volley_shot_time = self.last_volley_shot_tick / constants.FPS

        # Start a new volley if the interval has passed
        if current_time - last_shot_time >= constants.sniper_volley_interval:
            self.shots_fired_in_volley = 0
            self.last_volley_shot_tick = self.current_tick
            self.last_shot_tick = self.current_tick

        # Fire shots within the volley with scaled delay
        if self.shots_fired_in_volley < 3 and (current_time - last_volley_shot_time >= constants.sniper_shot_delay):
            from src.helpers import calculate_angle
            aim_angle = calculate_angle(self.x, self.y, target_x, target_y)

            # Apply scaled spread
            spread = constants.sniper_bullet_spread * game_state.scale  
            angle_offset = random.uniform(-spread, spread)
            aim_angle += angle_offset

            bullet = SniperEnemyBullet(
                x=self.x,
                y=self.y,
                angle=aim_angle,
                speed=constants.sniper_bullet_speed * game_state.scale,
            )

            game_state.projectiles.append(bullet)
            self.shots_fired_in_volley += 1
            self.last_volley_shot_tick = self.current_tick
