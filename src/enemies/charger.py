import math
from src.enemies.base import BaseEnemy
import src.constants as constants
import src.game_state as game_state

class ChargerEnemy(BaseEnemy):
    def __init__(self, x, y, scaling):
        super().__init__(x, y, scaling)
        
        # Set starting health based on scaling
        self._health = self.max_health
        self.score_reward = math.floor(constants.base_charger_xp_reward * self.scaling)
        
        self.damage_multiplier = 0.5

        # Movement properties (scaled once)
        self.acceleration = constants.CHARGER_ACCELERATION * game_state.scale
        self.max_speed = constants.CHARGER_MAX_SPEED * game_state.scale
        self.charge_speed = 22.0 * game_state.scale

        # Distances
        self.charge_distance = 250 * game_state.scale
        self.charge_distance_max = 900 * game_state.scale

        # Appearance attributes
        self.outline_size = constants.CHARGER_ENEMY_OUTLINE_SIZE * game_state.scale
        self.inner_size = constants.CHARGER_ENEMY_INNER_SIZE * game_state.scale
        self.outline_color = constants.CHARGER_ENEMY_OUTLINE_COLOR
        self.inner_color = constants.CHARGER_ENEMY_INNER_COLOR

        # Charging behavior
        self.charge_cooldown = 0
        self.charge_distance_traveled = 0
        self.charge_cooldown_duration = 30  # Cooldown duration (in frames)

        # Velocity
        self.vx = 0.0
        self.vy = 0.0

    @property
    def type(self):
        return "charger"

    @property
    def base_health(self):
        return constants.base_charger_health

    def shoot(self, target_x, target_y, game_state):
        pass  # Charger enemies do not shoot

    def update(self, target_x, target_y, game_state):
        """ Update movement and charge behavior """
        super().update(target_x, target_y, game_state)
        if self.dying:
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        # Compute unit vector toward player
        if distance > 0:
            desired_dir_x = dx / distance
            desired_dir_y = dy / distance
        else:
            desired_dir_x, desired_dir_y = 0.0, 0.0

        # Charging logic
        if self.charge_distance_traveled > 0:  
            remaining_distance = self.charge_distance_max - self.charge_distance_traveled
            if remaining_distance <= 300 * game_state.scale:
                # Slow down at the end of charge
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
            # During cooldown, stop moving
            self.charge_cooldown -= 1
            self.vx = 0
            self.vy = 0

        elif distance < self.charge_distance and self.charge_cooldown <= 0:
            # Start charging toward player
            self.charge_direction_x = desired_dir_x
            self.charge_direction_y = desired_dir_y
            self.vx = self.charge_direction_x * self.charge_speed
            self.vy = self.charge_direction_y * self.charge_speed
            self.charge_distance_traveled = math.hypot(self.vx, self.vy)

        else:
            # Normal movement (not charging)
            desired_vx = desired_dir_x * self.max_speed
            desired_vy = desired_dir_y * self.max_speed

            steer_x = desired_vx - self.vx
            steer_y = desired_vy - self.vy

            steer_magnitude = math.hypot(steer_x, steer_y)
            if steer_magnitude > self.acceleration:
                steer_x = (steer_x / steer_magnitude) * self.acceleration
                steer_y = (steer_y / steer_magnitude) * self.acceleration

            self.vx += steer_x
            self.vy += steer_y

        # Apply max speed limit
        max_speed = self.charge_speed if self.charge_distance_traveled > 0 else constants.CHARGER_NORMAL_SPEED * game_state.scale
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > max_speed:
            scale = max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep enemy within screen boundaries
        self._restrict_to_boundaries(game_state)

        # Check collision with player
        self.check_collision(game_state)

    def check_collision(self, game_state):
        """ Handle collision with player """
        if self.dying:
            return
        
        player = game_state.player
        player_radius = getattr(player, "collision_radius", 15)
        enemy_radius = self.inner_size / 2  # Enemy size is already scaled

        distance = math.hypot(self.x - player.x, self.y - player.y)
        if distance < (enemy_radius + player_radius):
            # Damage player and enemy on collision
            player.take_damage(self.health * self.damage_multiplier)
            if not player.is_dead():
                self.apply_damage(self.health, game_state)
                self.vx = 0
                self.vy = 0
