import math
from src.enemies.base import BaseEnemy
import src.engine.constants as constants
import src.engine.game_state as game_state

from src.engine.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor() # This ui_scaling_factor is calculated once and used throughout.


class ChargerEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        # Set starting health based on scaling
        self._health = self.max_health
        # Score reward based on a constant multiplier (make sure to define this in your constants)
        self.score_reward = math.floor(constants.base_charger_xp_reward * self.scaling)
        
        # For acceleration-based physics:
        self.vx = 0.0
        self.vy = 0.0
        # Already scaled:
        self.acceleration = constants.CHARGER_ACCELERATION * ui_scaling_factor 
        self.max_speed = constants.CHARGER_MAX_SPEED * ui_scaling_factor       
        
        # Appearance attributes (if you want to scale these, multiply them too):
        self.outline_size = constants.CHARGER_ENEMY_OUTLINE_SIZE  
        # If your outline size is defined in design pixels and you want it larger on lower-res screens,
        # you might do: self.outline_size = constants.CHARGER_ENEMY_OUTLINE_SIZE * ui_scaling_factor
        self.inner_size = constants.CHARGER_ENEMY_INNER_SIZE  
        # (Same note applies to inner_size if needed.)
        self.outline_color = constants.CHARGER_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.CHARGER_ENEMY_INNER_COLOR

        self.charge_cooldown = 0  # Cooldown timer for charging
        # Already scaled:
        self.charge_distance = 250 * ui_scaling_factor  # ← Good
        self.charge_speed = 20.0 * ui_scaling_factor      # ← Good
        self.charge_distance_max = 900 * ui_scaling_factor  # ← Good
        self.charge_distance_traveled = 0  # This accumulates; decide if you want it in design or scaled units.
        self.charge_cooldown_duration = 30  # Cooldown duration (0.7 seconds at 60 ticks per second)
        # (If CHARGER_NORMAL_SPEED is defined in design pixels, you might later want to use it scaled.)

    @property
    def type(self):
        return "charger"

    @property
    def base_health(self):
        return constants.base_charger_health

    def shoot(self, target_x, target_y, game_state):
        # The charger enemy does not shoot.
        pass
    
    def move(self, target_x, target_y, game_state):
        pass

    def update(self, target_x, target_y, game_state):
        """
        Update the charger enemy using a steering behavior that ensures it
        directly homes in on the player instead of orbiting when the player strafes.
        This method computes the desired velocity toward the player (scaled to max_speed)
        and then applies a steering force (difference between desired and current velocity)
        limited by the enemy's acceleration.
        """
        super().update(target_x, target_y, game_state)
        if self.dying:
            return
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        # Compute unit vector toward player
        if distance != 0:
            desired_dir_x = dx / distance
            desired_dir_y = dy / distance
        else:
            desired_dir_x, desired_dir_y = 0.0, 0.0

        # If the charger is currently charging
        # (If your charge_distance_traveled is already stored in scaled units, you might not need to multiply it here.)
        if self.charge_distance_traveled * ui_scaling_factor > 0:
            remaining_distance = self.charge_distance_max - self.charge_distance_traveled * ui_scaling_factor

            if remaining_distance <= 300 * ui_scaling_factor:
                # Stop abruptly with easing
                self.vx *= 0.5
                self.vy *= 0.5
                self.charge_distance_traveled = 0
                self.charge_cooldown = self.charge_cooldown_duration  # Start cooldown

            else:
                # Continue charging
                self.vx = self.charge_direction_x * self.charge_speed
                self.vy = self.charge_direction_y * self.charge_speed
                self.charge_distance_traveled += math.hypot(self.vx, self.vy)

        elif self.charge_cooldown > 0:
            # Cooldown phase: Stop moving entirely
            self.charge_cooldown -= 1
            self.vx = 1  # These values (1) are not scaled; if needed, consider: 1 * ui_scaling_factor
            self.vy = 1

        elif distance < self.charge_distance and self.charge_cooldown <= 0:
            # Start charging if within range and off cooldown
            self.charge_direction_x = desired_dir_x
            self.charge_direction_y = desired_dir_y
            self.vx = self.charge_direction_x * self.charge_speed
            self.vy = self.charge_direction_y * self.charge_speed
            self.charge_distance_traveled += math.hypot(self.vx, self.vy)

        else:
            # Normal movement toward player (non-charging phase)
            desired_vx = desired_dir_x * self.max_speed
            desired_vy = desired_dir_y * self.max_speed

            steer_x = desired_vx - self.vx
            steer_y = desired_vy - self.vy
            max_acceleration = self.acceleration  # Already scaled
            steer_magnitude = math.hypot(steer_x, steer_y)

            if steer_magnitude > max_acceleration:
                steer_x = (steer_x / steer_magnitude) * max_acceleration
                steer_y = (steer_y / steer_magnitude) * max_acceleration

            self.vx += steer_x
            self.vy += steer_y

        if self.charge_distance_traveled > 0:  # If currently charging
            max_speed = self.charge_speed  # Keep charge speed high
        else:
            # Here, if constants.CHARGER_NORMAL_SPEED is defined in design pixels,
            # you may want to scale it:
            # max_speed = constants.CHARGER_NORMAL_SPEED * ui_scaling_factor
            max_speed = constants.CHARGER_NORMAL_SPEED

        # Apply max speed cap
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > max_speed:
            scale = max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep the enemy within screen boundaries
        self._restrict_to_boundaries(game_state)

        # Check for collisions with the player
        self.check_collision(game_state)

    def check_collision(self, game_state):
        """
        Check if the enemy has collided with the player.
        If a collision is detected, deal contact damage to the player equal to the enemy's current health,
        then deduct that same amount from its own health.
        """
        player = game_state.player
        player_radius = getattr(player, "collision_radius", 15)
        enemy_radius = self.inner_size / 2  # If inner_size is in design pixels and you want it larger on lower-res, multiply if needed.

        distance = math.hypot(self.x - player.x, self.y - player.y)
        if distance < (enemy_radius + player_radius):
            # Apply contact damage to the player. (nerfed damage)
            player.take_damage((player.max_health * constants.CHARGER_MAX_HP_DAMAGE) + (constants.CHARGER_BASE_DAMAGE))
            # The enemy deducts the damage dealt from its own health.
            # This call to apply_damage will also handle adding damage numbers and score rewards.
            if not player.is_dead():
                self.apply_damage(self.health, game_state)
                self.vx = 0
                self.vy = 0
