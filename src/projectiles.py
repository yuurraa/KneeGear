from enum import Enum
from dataclasses import dataclass
import pygame
import math
import game_state
import constants
import score
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
    size: float = 5.0
    scaling: float = 1.0
    
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
        return (self.x < 0 or self.x > game_state.screen_width or
                self.y < 0 or self.y > game_state.screen_height - constants.experience_bar_height - 3)

    def check_and_apply_collision(self, target) -> bool:
        raise NotImplementedError("check_collision method must be implemented in subclasses")

@dataclass
class PlayerBaseBullet(BaseBullet):
    def __init__(self, x: float, y: float, angle: float, speed: float, damage: float, pierce: int, size: float, colour: Tuple[int, int, int]):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            alignment=Alignment.PLAYER,
            speed=speed,
            damage=damage,
            size=size,
            colour=colour,
            pierce=pierce
        )


    def check_and_apply_collision(self, enemy) -> bool:
        if (enemy.health > 0 and
            pygame.Rect(enemy.x - 20, enemy.y - 20, 40, 40).colliderect(self.get_rect())):
            self.pierce -= 1
            enemy.apply_damage(self.damage, game_state)
            return True

        return False

class PlayerBasicBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, basic_bullet_damage_multiplier: float, basic_bullet_speed_multiplier: float):
        super().__init__(x, y, angle, 
                        constants.player_basic_bullet_speed * basic_bullet_speed_multiplier,
                        constants.player_basic_bullet_damage * basic_bullet_damage_multiplier,
                        constants.player_basic_bullet_pierce,
                        constants.player_basic_bullet_size,
                        constants.BLUE)
        
class PlayerSpecialBullet(PlayerBaseBullet):
    def __init__(self, x: float, y: float, angle: float, special_bullet_damage_multiplier: float, special_bullet_speed_multiplier: float):
        super().__init__(x, y, angle,
                         constants.player_special_bullet_speed * special_bullet_speed_multiplier,
                         constants.player_special_bullet_damage * special_bullet_damage_multiplier,
                         constants.player_special_bullet_pierce,
                         constants.player_special_bullet_size,
                         constants.PURPLE)

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
        if pygame.Rect(game_state.player.x - 15, game_state.player.y - 15, 30, 30).colliderect(self.get_rect()):
            actual_damage = math.floor(self.damage * self.scaling)
            game_state.player.health -= actual_damage
            
            game_state.damage_numbers.append({
                "x": game_state.player.x,
                "y": game_state.player.y,
                "value": actual_damage,
                "timer": 60,
                "color": constants.RED
            })
            return True
        return False

@dataclass
class TankEnemyBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, speed: float, angle: float):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=speed,
            base_damage=constants.base_tank_damage,
            size=3,
            colour=constants.BROWN
        )

@dataclass
class BasicEnemyBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=constants.basic_enemy_bullet_speed,
            base_damage=constants.base_basic_enemy_damage,
            size=5,
            colour=constants.RED
        )

class BasicEnemyHomingBullet(BaseEnemyBullet):
    def __init__(self, x: float, y: float, angle: float, is_special: bool = False):
        super().__init__(
            x=x,
            y=y,
            angle=angle,
            speed=constants.basic_enemy_homing_bullet_speed,
            base_damage=constants.base_basic_enemy_damage,
            size=5,
            colour=constants.RED
        )
        self.spawn_time: float = pygame.time.get_ticks() / 1000.0
    
    def should_home(self) -> bool:
        current_time = pygame.time.get_ticks() / 1000.0
        return (current_time - self.spawn_time) < 1
        
    def update(self):
        super().update()
        if self.should_home():
            from helpers import calculate_angle
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