from enum import Enum
import pygame
import math

from projectiles import PlayerBasicBullet, PlayerSpecialBullet
from helpers import calculate_angle
import constants

class PlayerState(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    LEVELING_UP = "leveling_up"

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        # Position
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.angle = 0  # Add angle property
        
        self.reset()

    def reset(self):
        # Stats
        self.health:float = constants.base_player_health
        self.max_health = constants.base_player_health
        self.hp_regen = constants.base_player_hp_regen_percent #hp regen percent per second
        self.speed = constants.player_speed
        self.player_experience = 0
        self.player_level = 1
        self.experience_to_next_level = constants.initial_experience_to_next_level
        
        self.ticks_since_last_hp_regen = 0
        #upgrades
        self.basic_bullet_damage_multiplier = 1
        self.special_bullet_damage_multiplier = 1
        self.basic_bullet_speed_multiplier = 1
        self.special_bullet_speed_multiplier = 1
        self.hp_regen_percent_bonus = 0
        self.hp_pickup_healing_percent_bonus = 0
        self.basic_bullet_piercing_bonus = 0
        self.special_bullet_piercing_bonus = 0
        self.special_bullet_can_repierce = False
        self.hp_steal = 0
        
        self.state = PlayerState.ALIVE
        
        # Shooting cooldowns
        self.shoot_cooldown = constants.player_basic_bullet_cooldown  # Regular shot cooldown in seconds
        self.special_shot_cooldown = constants.player_special_bullet_cooldown  # Special shot cooldown in seconds
        self.last_shot_time = 0
        self.last_special_shot_time = 0

        self.applied_upgrades = set()  # Tracks names of applied upgrades
    
    def draw(self, screen):
        # Draw player body
        pygame.draw.rect(screen, constants.BLACK, (self.x - 16, self.y - 16, 22, 22))  # Outline
        pygame.draw.rect(screen, constants.GREEN, (self.x - 15, self.y - 15, 20, 20))
        
        # Draw direction arrow
        arrow_length = 20
        arrow_x = self.x + arrow_length * math.cos(math.radians(self.angle))
        arrow_y = self.y + arrow_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, constants.BLUE, (self.x, self.y), (arrow_x, arrow_y), 3)

        # Draw health bar
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen, bar_width=100, bar_height=10):
        x = 20  # Fixed position for health bar
        y = 20
        filled_width = int((self.health / self.max_health) * bar_width)
        surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, constants.BLACK, (0, 0, bar_width, bar_height))
        pygame.draw.rect(surface, constants.TRANSLUCENT_GREEN, (0, 0, filled_width, bar_height))
        screen.blit(surface, (x, y))

    def update_angle(self, mouse_pos):
        mx, my = mouse_pos
        self.angle = calculate_angle(self.x, self.y, mx, my)
        
    def move(self, keys):
        # Calculate new position first
        new_x, new_y = self.x, self.y

        if keys[pygame.K_w]:
            new_y -= self.speed
        if keys[pygame.K_s]:
            new_y += self.speed
        if keys[pygame.K_a]:
            new_x -= self.speed
        if keys[pygame.K_d]:
            new_x += self.speed

        # Restrict player to screen boundaries
        self.x = max(15, min(new_x, self.screen_width - 15))
        self.y = max(15, min(new_y, self.screen_height - 15))

    def update_hp_regen(self):
        self.ticks_since_last_hp_regen += 1
        if self.ticks_since_last_hp_regen >= constants.FPS:
            regen_amount = (self.max_health * (self.hp_regen + self.hp_regen_percent_bonus) / 100)
            self.heal(regen_amount)
            self.ticks_since_last_hp_regen = 0
    
    def update(self, keys):
        if self.state == PlayerState.DEAD:
            return
        self.update_hp_regen()
        self.move(keys)

    def shoot_regular(self, mouse_pos, current_time):
        """Regular shot (left-click)"""
        if (self.state == PlayerState.DEAD or 
            current_time - self.last_shot_time < self.shoot_cooldown):
            return None

        mx, my = mouse_pos
        angle = calculate_angle(self.x, self.y, mx, my)
        self.last_shot_time = current_time
        return PlayerBasicBullet(self.x, self.y, angle, self.basic_bullet_damage_multiplier, self.basic_bullet_speed_multiplier, self.basic_bullet_piercing_bonus)

    def shoot_special(self, mouse_pos, current_time):
        """Special shot (right-click)"""
        if (self.state == PlayerState.DEAD or 
            current_time - self.last_special_shot_time < self.special_shot_cooldown):
            return None

        mx, my = mouse_pos
        angle = calculate_angle(self.x, self.y, mx, my)
        self.last_special_shot_time = current_time
        return PlayerSpecialBullet(self.x, self.y, angle, self.special_bullet_damage_multiplier, self.special_bullet_speed_multiplier, self.special_bullet_piercing_bonus, self.special_bullet_can_repierce)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.state = PlayerState.DEAD

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def heal_from_pickup(self):
        # Change from fixed amount to percentage of max health
        heal_amount = self.max_health * ((self.hp_pickup_healing_percent_bonus+constants.base_hp_pickup_healing_percent) / 100)
        self.heal(heal_amount)
        return heal_amount
        

    def get_cooldown_progress(self, current_time):
        """Returns the cooldown progress for both abilities (0.0 to 1.0)"""
        regular_progress = max(0, (current_time - self.last_shot_time) / self.shoot_cooldown)
        special_progress = max(0, (current_time - self.last_special_shot_time) / self.special_shot_cooldown)
        return regular_progress, special_progress 
    
    def gain_experience(self, amount):
        self.player_experience += amount
        if self.player_experience >= self.experience_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.player_level += 1
        self.player_experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * constants.level_up_xp_cost_scaling_factor)
        self.state = PlayerState.LEVELING_UP
        print(f"Player leveled up to level {self.player_level}")
            


    def apply_upgrade(self, upgrade):
        upgrade.apply(self)
        self.applied_upgrades.add(upgrade.name)

    # def reset