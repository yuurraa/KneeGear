import math
from src.enemies.base import BaseEnemy
import src.constants as constants

class ChargerEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        # Set starting health based on scaling
        self._health = self.max_health
        # Score reward based on a constant multiplier (make sure to define this in your constants)
        self.score_reward = math.floor(constants.base_charger_xp_reward * self.scaling)
        
        self.damage_multiplier = 0.4
        
        # For acceleration-based physics:
        self.vx = 0.0
        self.vy = 0.0
        self.acceleration = constants.CHARGER_ACCELERATION  # e.g., 0.2 or any suitable value
        self.max_speed = constants.CHARGER_MAX_SPEED
        
        # Appearance attributes
        self.outline_size = constants.CHARGER_ENEMY_OUTLINE_SIZE
        self.inner_size = constants.CHARGER_ENEMY_INNER_SIZE
        self.outline_color = constants.CHARGER_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.CHARGER_ENEMY_INNER_COLOR

        self.charge_cooldown = 0  # Cooldown timer for charging
        self.charge_distance = 200  # Increased distance within which the enemy will charge
        self.charge_speed = 13.0  # Speed during the charge
        self.charge_distance_max = 400  # Maximum distance the enemy can charge
        self.charge_distance_traveled = 0  # Distance traveled during the current charge
        self.charge_cooldown_duration = 0  # Cooldown duration (0.7 seconds at 60 ticks per second)

    @property
    def type(self):
        return "charger"

    @property
    def base_health(self):
        return constants.base_charger_health

    def shoot(self, target_x, target_y, current_tick, game_state):
        # The charger enemy does not shoot.
        pass

    def update(self, target_x, target_y, current_tick, game_state):
        """
        Update the charger enemy using a steering behavior that ensures it
        directly homes in on the player instead of orbiting when the player strafes.
        This method computes the desired velocity toward the player (scaled to max_speed)
        and then applies a steering force (difference between desired and current velocity)
        limited by the enemy's acceleration.
        """
        # Calculate vector from enemy to target (player)
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        
        # If the enemy is exactly at the player's position, there's no steering needed.
        if distance != 0:
            # Compute the unit vector in the direction of the player
            desired_dir_x = dx / distance
            desired_dir_y = dy / distance
        else:
            desired_dir_x, desired_dir_y = 0.0, 0.0
        
        # Desired velocity is in the direction of the player scaled to the max speed
        desired_vx = desired_dir_x * self.max_speed
        desired_vy = desired_dir_y * self.max_speed

        # Steering force is the difference between the desired velocity and the current velocity
        steer_x = desired_vx - self.vx
        steer_y = desired_vy - self.vy
        steer_magnitude = math.hypot(steer_x, steer_y)
        
        # Limit the steering force to the maximum acceleration
        if steer_magnitude > 0:
            scale = min(1, self.acceleration / steer_magnitude)
            steer_x *= scale
            steer_y *= scale

        # Apply the steering force to the current velocity
        self.vx += steer_x
        self.vy += steer_y

        # Check if the enemy can charge
        if self.charge_cooldown <= 0 and distance < self.charge_distance:
            # Start charging towards the player
            if self.charge_distance_traveled == 0:  # Only set direction on the first charge
                self.charge_direction_x = desired_dir_x
                self.charge_direction_y = desired_dir_y
            
            # Calculate the distance remaining to the max charge distance
            remaining_distance = self.charge_distance_max - self.charge_distance_traveled
            
            # Slow down as it approaches the end of the charge
            if remaining_distance < 20:  # Adjust this threshold as needed
                # Gradually reduce speed
                speed_factor = remaining_distance / 20  # Scale speed down to 0 as it approaches the end
                self.vx = self.charge_direction_x * self.charge_speed * speed_factor
                self.vy = self.charge_direction_y * self.charge_speed * speed_factor
            else:
                self.vx = self.charge_direction_x * self.charge_speed
                self.vy = self.charge_direction_y * self.charge_speed
            
            self.charge_distance_traveled += math.hypot(self.vx, self.vy)  # Increment the distance traveled
            
            if self.charge_distance_traveled >= self.charge_distance_max:
                self.charge_cooldown = self.charge_cooldown_duration  # Set cooldown after reaching max charge distance
                self.charge_distance_traveled = 0  # Reset distance traveled after charge
        else:
            # Apply cooldown
            if self.charge_cooldown > 0:
                self.charge_cooldown -= 1
                self.vx = 0  # Stop moving during cooldown
                self.vy = 0  # Stop moving during cooldown
            else:
                # Reset distance if not charging
                self.charge_distance_traveled = 0  # Ensure distance is reset when not charging
        
        # After updating, ensure that velocity does not exceed the max speed
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # Update the enemy's position based on the new velocity
        self.x += self.vx
        self.y += self.vy

        # Keep the enemy within screen boundaries
        self._restrict_to_boundaries(game_state)

        # Check for collisions with the player to apply contact damage
        self.check_collision(game_state)

    def check_collision(self, game_state):
        """
        Check if the enemy has collided with the player.
        If a collision is detected, deal contact damage to the player equal to the enemy's current health,
        then deduct that same amount from its own health.
        """
        player = game_state.player
        player_radius = getattr(player, "collision_radius", 15)
        enemy_radius = self.inner_size / 2

        distance = math.hypot(self.x - player.x, self.y - player.y)
        if distance < (enemy_radius + player_radius):
            # Collision detected!
            # Instead of dealing damage, bounce away from the player
            bounce_back_x = self.x - player.x
            bounce_back_y = self.y - player.y
            bounce_back_distance = 20  # Distance to bounce back
            self.x += bounce_back_x / distance * bounce_back_distance
            self.y += bounce_back_y / distance * bounce_back_distance
            
            # Apply contact damage to the player. (nerfed damage)
            player.take_damage(self.health * self.damage_multiplier)
            # The enemy deducts the damage dealt from its own health.
            # This call to apply_damage will also handle adding damage numbers and score rewards.
            if not player.is_dead():
                self.apply_damage(self.health, game_state) 