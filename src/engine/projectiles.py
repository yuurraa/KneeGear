from enum import Enum
from dataclasses import dataclass
import pygame
import math
import src.engine.game_state as game_state
import src.engine.constants as constants
from src.engine.helpers import get_ui_scaling_factor
from src.player.skins import ProjectileSkin

ui_scaling_factor = get_ui_scaling_factor()

from typing import Tuple

class Alignment(Enum):
    PLAYER = "player"
    ENEMY = "enemy"

@dataclass
class BaseBullet:
    x: float
    y: float
    angle: float
    alignment: Alignment
    speed: float
    damage: float
    colour: Tuple[int, int, int]
    pierce: int = 1
    can_repierce: bool = False  # whether the bullet can hit the same target multiple times
    size: float = 5.0 * ui_scaling_factor
    scaling: float = 1.0 * ui_scaling_factor
    initial_x: float = 0
    initial_y: float = 0
    active: bool = True  # NEW: flag to indicate if bullet is in use

    def __post_init__(self):
        self.hit_targets = set()  # Track which targets have been hit

    def update(self):
        if not self.active:
            return  # Skip update if bullet is not active

        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        
        # Check if bullet is out of bounds first
        if self.is_out_of_bounds():
            self.deactivate()
            return
        
        # Check for collisions based on alignment
        if self.alignment == Alignment.PLAYER:
            for enemy in game_state.enemies[:]:  # Use slice copy to avoid modification during iteration
                if self.check_and_apply_collision(enemy):
                    if self.pierce <= 0:
                        self.deactivate()
                    break
        elif self.alignment == Alignment.ENEMY:
            if self.check_and_apply_collision(game_state.player):
                self.deactivate()
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), int(self.size))
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
        
    def get_position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def is_out_of_bounds(self) -> bool:
        return (self.x < 0 or self.x > game_state.screen_width or
                self.y < 0 or self.y > game_state.screen_height)

    def check_and_apply_collision(self, target) -> bool:
        raise NotImplementedError("check_collision method must be implemented in subclasses")

    def deactivate(self):
        """Mark this bullet as inactive so it can be recycled."""
        self.active = False

    def reset(self, *args, **kwargs):
        """
        Reset the bullet's properties.
        Additional keyword arguments can update bullet-specific attributes.
        """
        self.__init__(*args, **kwargs)

class BulletPool:
    def __init__(self):
        self.pool = []  # Holds all bullet objects (active and inactive)

    def get_bullet(self, bullet_class, *args, **kwargs):
        """
        Retrieve an inactive bullet of the specified class from the pool.
        If none is available, create a new one.
        The args/kwargs are the parameters for the bullet's constructor.
        """
        # Look for an inactive bullet of the same type.
        for bullet in self.pool:
            if isinstance(bullet, bullet_class) and not bullet.active:
                bullet.reset(*args, **kwargs)
                return bullet
        # If none found, create a new bullet.
        bullet = bullet_class(*args, **kwargs)
        self.pool.append(bullet)
        return bullet

    def update(self):
        """Update all active bullets."""
        for bullet in self.pool:
            if bullet.active:
                bullet.update()

    def draw(self, screen):
        """Draw all active bullets."""
        for bullet in self.pool:
            if bullet.active:
                bullet.draw(screen)
@dataclass
class PlayerBaseBullet(BaseBullet):
    # New attribute for projectile skin.
    projectile_skin: 'ProjectileSkin' = None  # type: ignore

    def __init__(self, x: float, y: float, angle: float, speed: float, damage: float, pierce: int,
                 can_repierce: bool, size: float, colour: Tuple[int, int, int],
                 projectile_skin=None):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            alignment=Alignment.PLAYER,
            speed=speed * ui_scaling_factor,
            damage=damage,
            size=size * ui_scaling_factor,
            colour=colour,
            pierce=pierce,
            can_repierce=can_repierce
        )
        self.projectile_skin = projectile_skin

    def draw(self, screen):
        if self.active:
            if self.projectile_skin:
                # Update and draw the projectile skin.
                self.projectile_skin.update()
                self.projectile_skin.draw(screen, int(self.x), int(self.y), int(self.size))
            else:
                pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), int(self.size))
    
    def compute_scaled_damage(self) -> float:
        if getattr(self, "scales_with_distance_travelled", False):
            travel_distance = math.hypot(self.x - self.initial_x, self.y - self.initial_y)
            if isinstance(self, PlayerBasicBullet):
                bonus_multiplier = (min(travel_distance, 800) / 800) * 2
            elif isinstance(self, PlayerSpecialBullet):
                if travel_distance >= 500:
                    bonus_multiplier = 0
                elif travel_distance <= 50:
                    bonus_multiplier = 2
                else:
                    bonus_multiplier = ((500 - travel_distance) / 450 * 2)
            else:
                bonus_multiplier = 0
            return self.damage * (1 + bonus_multiplier)
        else:
            return self.damage

    def check_and_apply_collision(self, enemy) -> bool:
        if (enemy.health > 0 and
            pygame.Rect(enemy.x - 20, enemy.y - 20, 40, 40).colliderect(self.get_rect())):
            
            if not self.can_repierce and enemy in self.hit_targets:
                return False
                
            self.pierce -= 1
            actual_damage = self.compute_scaled_damage()
            enemy.apply_damage(actual_damage, game_state)
            game_state.player.heal(actual_damage * game_state.player.hp_steal)
            self.hit_targets.add(enemy)
            return True

        return False

class PlayerBasicBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, base_damage_multiplier: float,
                 basic_bullet_damage_multiplier: float, basic_bullet_speed_multiplier: float,
                 basic_bullet_piercing_multiplier: float, scales_with_distance_travelled: bool = False,
                 can_repierce: bool=False, projectile_skin=None):
        super().__init__(
            x, y, angle,
            constants.player_basic_bullet_speed * basic_bullet_speed_multiplier * ui_scaling_factor,
            constants.player_basic_bullet_damage * base_damage_multiplier * basic_bullet_damage_multiplier,
            math.ceil(constants.player_basic_bullet_pierce * basic_bullet_piercing_multiplier),
            can_repierce,
            constants.player_basic_bullet_size * ui_scaling_factor,
            constants.BLUE,
            projectile_skin=projectile_skin
        )
        self.scales_with_distance_travelled = scales_with_distance_travelled
        if scales_with_distance_travelled:
            self.initial_x = x
            self.initial_y = y

class PlayerSpecialBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, base_damage_multiplier: float,
                 special_bullet_damage_multiplier: float, special_bullet_damage_bonus: float,
                 special_bullet_speed_multiplier: float, special_bullet_piercing_multiplier: float,
                 special_bullet_radius_multiplier: float, scales_with_distance_travelled: bool = False,
                 can_repierce: bool=False, projectile_skin=None):
        super().__init__(
            x, y, angle,
            constants.player_special_bullet_speed * special_bullet_speed_multiplier * ui_scaling_factor,
            constants.player_special_bullet_damage * base_damage_multiplier * special_bullet_damage_multiplier + special_bullet_damage_bonus,
            math.ceil(constants.player_special_bullet_pierce * special_bullet_piercing_multiplier),
            can_repierce,
            constants.player_special_bullet_size * special_bullet_radius_multiplier * ui_scaling_factor,
            constants.PURPLE,
            projectile_skin=projectile_skin
        )
        self.scales_with_distance_travelled = scales_with_distance_travelled
        if scales_with_distance_travelled:
            self.initial_x = x
            self.initial_y = y

@dataclass
class BaseEnemyBullet(BaseBullet):
    def __init__(self, x: float, y: float, angle: float, speed: float, base_damage: float,  colour: Tuple[int, int, int], size: float=constants.base_enemy_bullet_size * ui_scaling_factor):
        damage = base_damage * game_state.enemy_scaling
        
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            alignment=Alignment.ENEMY,
            speed=speed * ui_scaling_factor,
            damage=damage,
            size=size * ui_scaling_factor,
            colour=colour,
            pierce=1
        )
    def check_and_apply_collision(self, target) -> bool:
        # Use player's size attribute for collision detection
        if pygame.Rect(game_state.player.x - game_state.player.size/2, 
                      game_state.player.y - game_state.player.size/2, 
                      game_state.player.size, 
                      game_state.player.size).colliderect(self.get_rect()):
            actual_damage = math.floor(self.damage * self.scaling)
            game_state.player.take_damage(actual_damage)
        
            return True
        return False

@dataclass
class TankEnemyBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, speed: float, angle: float):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=speed * ui_scaling_factor,
            base_damage=constants.base_tank_damage,
            size=constants.tank_bullet_size * ui_scaling_factor,
            colour=constants.BROWN
        )

@dataclass
class BasicEnemyBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=constants.basic_enemy_bullet_speed * ui_scaling_factor,
            base_damage=constants.base_basic_enemy_damage,
            colour=constants.RED,
        )

class BasicEnemyHomingBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, angle: float, is_special: bool = False):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=constants.basic_enemy_homing_bullet_speed * ui_scaling_factor,
            base_damage=constants.base_basic_enemy_damage,
            colour=constants.RED
        )
        self.spawn_time: float = pygame.time.get_ticks() / 1000.0
    
    def should_home(self) -> bool:
        current_time = pygame.time.get_ticks() / 1000.0
        return (current_time - self.spawn_time) < 1
        
    def update(self):
        super().update()
        if self.should_home():
            from src.engine.helpers import calculate_angle
            angle_to_player = calculate_angle(self.x, self.y, game_state.player.x, game_state.player.y)
            angle_diff = angle_to_player - self.angle
            
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            
            if abs(angle_diff) > constants.basic_enemy_bullet_max_turn_angle:
                angle_diff = (constants.basic_enemy_bullet_max_turn_angle 
                            if angle_diff > 0 
                            else -constants.basic_enemy_bullet_max_turn_angle)
            
            self.angle += angle_diff

@dataclass
class SniperEnemyBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, speed: float, angle: float):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=speed * ui_scaling_factor,
            base_damage=constants.sniper_bullet_damage,
            colour=constants.PURPLE
        )
