from enum import Enum
from dataclasses import dataclass
import pygame
import math
import src.game_state as game_state
import src.constants as constants
import src.score as score
from src.helpers import get_ui_scaling_factor

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
    can_repierce: bool = False #whether the bullet can hit the same target multiple times
    size: float = 5.0 * ui_scaling_factor
    scaling: float = 1.0 * ui_scaling_factor
    initial_x: float = 0
    initial_y: float = 0
    

    def __post_init__(self):
        self.hit_targets = set()  # Track which targets have been hit
    
    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        
        # Check if bullet is out of bounds first
        if self.is_out_of_bounds():
            game_state.projectiles.remove(self)
            return
        
        # Check for collisions based on alignment
        if self.alignment == Alignment.PLAYER:
            for enemy in game_state.enemies[:]:  # Use slice copy to avoid modification during iteration
                if self.check_and_apply_collision(enemy):
                    if self.pierce <= 0:
                        game_state.projectiles.remove(self)
                    break
                
            
        elif self.alignment == Alignment.ENEMY:
            if self.check_and_apply_collision(game_state.player):
                game_state.projectiles.remove(self)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), int(self.size))
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
        
    def get_position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def is_out_of_bounds(self) -> bool:
        return (self.x < 0 or self.x > game_state.DESIGN_WIDTH or
                self.y < 0 or self.y > game_state.DESIGN_HEIGHT - constants.experience_bar_height - 3)

    def check_and_apply_collision(self, target) -> bool:
        raise NotImplementedError("check_collision method must be implemented in subclasses")

@dataclass
class PlayerBaseBullet(BaseBullet):
    def __init__(self, x: float, y: float, angle: float, speed: float, damage: float, pierce: int, can_repierce: bool, size: float, colour: Tuple[int, int, int]):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            alignment=Alignment.PLAYER,
            speed=speed,
            damage=damage,
            size=size,
            colour=colour,
            pierce=pierce,
            can_repierce=can_repierce
        )

    def compute_scaled_damage(self) -> float:
        # Only modify damage if the bullet was marked to scale with distance.
        if getattr(self, "scales_with_distance_travelled", False):
            travel_distance = math.hypot(self.x - self.initial_x, self.y - self.initial_y)
            if isinstance(self, PlayerBasicBullet):
                # For a basic bullet: bonus scales up linearly, up to +200% bonus damage at 800px.
                bonus_multiplier = (min(travel_distance, 800) / 800) * 2
            elif isinstance(self, PlayerSpecialBullet):
                # For a special bullet: bonus of +200% at <=50px that drops to 0 bonus past 500px.
                if travel_distance >= 500:
                    bonus_multiplier = 0
                elif travel_distance <= 50:
                    bonus_multiplier = 2  # Full 200% bonus
                else:
                    bonus_multiplier = ((500 - travel_distance) / 450 * 2)  # Linear falloff from 50px to 500px
            else:
                bonus_multiplier = 0
            return self.damage * (1 + bonus_multiplier)
        else:
            return self.damage

    def check_and_apply_collision(self, enemy) -> bool:
        if (enemy.health > 0 and
            pygame.Rect(enemy.x - 20, enemy.y - 20, 40, 40).colliderect(self.get_rect())):
            
            # Check if we've already hit this enemy and can't repierce
            if not self.can_repierce and enemy in self.hit_targets:
                return False
                
            self.pierce -= 1
            actual_damage = self.compute_scaled_damage()
            enemy.apply_damage(actual_damage, game_state)
            game_state.player.heal(actual_damage * game_state.player.hp_steal)
            self.hit_targets.add(enemy)  # Track that we've hit this enemy
            return True

        return False

class PlayerBasicBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, base_damage_multiplier: float, basic_bullet_damage_multiplier: float, basic_bullet_speed_multiplier: float, basic_bullet_piercing_multiplier: float, scales_with_distance_travelled: bool = False, can_repierce: bool=False):
        super().__init__(x, y, angle, 
                         constants.player_basic_bullet_speed * basic_bullet_speed_multiplier * ui_scaling_factor,
                         constants.player_basic_bullet_damage * base_damage_multiplier * basic_bullet_damage_multiplier,
                         math.ceil(constants.player_basic_bullet_pierce * basic_bullet_piercing_multiplier),
                         can_repierce,
                         constants.player_basic_bullet_size * ui_scaling_factor,
                         constants.BLUE)
        self.scales_with_distance_travelled = scales_with_distance_travelled
        if scales_with_distance_travelled:
            # Record the starting position so that future updates can compute distance travelled.
            self.initial_x = x
            self.initial_y = y

class PlayerSpecialBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, base_damage_multiplier: float, special_bullet_damage_multiplier: float, special_bullet_damage_bonus: float, special_bullet_speed_multiplier: float, special_bullet_piercing_multiplier: float, special_bullet_radius_multiplier: float, scales_with_distance_travelled: bool = False, can_repierce: bool=False):
        super().__init__(x, y, angle,
                         constants.player_special_bullet_speed * special_bullet_speed_multiplier * ui_scaling_factor,
                         constants.player_special_bullet_damage * base_damage_multiplier * special_bullet_damage_multiplier + special_bullet_damage_bonus,
                         math.ceil(constants.player_special_bullet_pierce * special_bullet_piercing_multiplier),
                         can_repierce,
                         constants.player_special_bullet_size * special_bullet_radius_multiplier * ui_scaling_factor,
                         constants.PURPLE)
        self.scales_with_distance_travelled = scales_with_distance_travelled
        if scales_with_distance_travelled:
            # Store the starting position to measure travel distance.
            self.initial_x = x
            self.initial_y = y

@dataclass
class BaseEnemyBullet(BaseBullet):
    def __init__(self, x: float, y: float, angle: float, speed: float, base_damage: float, size: float, colour: Tuple[int, int, int]):
        damage = base_damage * game_state.enemy_scaling
        
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            alignment=Alignment.ENEMY,
            speed=speed,
            damage=damage,
            size=size,
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
            size=3 * ui_scaling_factor,
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
            size=5 * ui_scaling_factor,
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
            size=5 * ui_scaling_factor,
            colour=constants.RED
        )
        self.spawn_time: float = pygame.time.get_ticks() / 1000.0
    
    def should_home(self) -> bool:
        current_time = pygame.time.get_ticks() / 1000.0
        return (current_time - self.spawn_time) < 1
        
    def update(self):
        super().update()
        if self.should_home():
            from src.helpers import calculate_angle
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
            size=5 * ui_scaling_factor,
            colour=constants.PURPLE
        )
