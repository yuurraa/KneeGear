from enum import Enum
import pygame
import math

from src.projectiles import PlayerBasicBullet, PlayerSpecialBullet
from src.helpers import calculate_angle
import src.constants as constants

# Constants for the barrier shield
barrier_shield_hp_fraction = constants.BARRIER_SHIELD_HP_FRACTION
barrier_shield_regeneration_time = constants.BARRIER_SHIELD_REGENERATION_TIME

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
        self.size = 25  # Base size of the player square
        self.health: float = constants.base_player_health
        self.max_health = constants.base_player_health
        self.hp_regen = constants.base_player_hp_regen_percent  # hp regen percent per second
        self.speed = constants.player_speed
        self.player_experience = 0
        self.player_level = 1
        self.experience_to_next_level = constants.initial_experience_to_next_level
        
        self.ticks_since_last_hp_regen = 0
        self.current_tick = 0  # Add tick counter
        #upgrades
        self.base_damage_multiplier = 1
        self.basic_bullet_damage_multiplier = 1
        self.special_bullet_damage_multiplier = 1
        
        self.basic_bullet_speed_multiplier = 1
        self.special_bullet_speed_multiplier = 1
        
        self.basic_bullet_piercing_multiplier = 1.0  # default multiplier, i.e. no extra piercing
        self.special_bullet_piercing_multiplier = 1.0
        
        self.hp_regen_percent_bonus = 0
        
        self.max_pickups_on_screen = 1
        self.hp_pickup_healing_percent_bonus = 0
        self.hp_pickup_damage_boost_duration_s = 20
        self.hp_pickup_damage_boost_percent_bonus = 0
        self.hp_pickup_permanent_hp_boost_percent_bonus = 0
        self.hp_pickup_permanent_damage_boost_percent_bonus = 0

        self.special_bullet_radius_multiplier = 1.0
        self.special_bullet_can_repierce = False
        self.basic_bullet_extra_projectiles_per_shot_bonus = 0
        self.damage_reduction_percent_bonus = 0
        self.hp_steal = 0

        self.xp_gain_percent_bonus = 0
        self.rage_percent_bonus = 0 # percent damage gain per enemy on screen
        self.frenzy_percent_bonus = 0 # percent damage gain per projectile on screen
        self.fear_percent_bonus = 0 # max percent damage gain based on how low your hp is

        self.state = PlayerState.ALIVE
        
        # Shooting cooldowns
        self.shoot_cooldown = constants.player_basic_bullet_cooldown  # Regular shot cooldown in seconds
        self.special_shot_cooldown = constants.player_special_bullet_cooldown  # Special shot cooldown in seconds
        self.last_shot_time = 0
        self.last_special_shot_time = 0

        self.applied_upgrades = set()  # Tracks names of applied upgrades
        self.upgrade_levels = {}  # Tracks number of times each upgrade has been applied
        self.active_buffs = {}  # Dictionary to store active buffs and their end ticks (not times)
        self.barrier_shield_active = False
        self.barrier_shield_hp = 0
        self.barrier_shield_regeneration_time = 0  # Timer for shield regeneration
        self.base_speed = 5.0  # Define a base speed
        self.speed = self.base_speed
    
    def draw(self, screen):
        # Draw player body
        outline_offset = 1
        pygame.draw.rect(screen, constants.BLACK, 
                        (self.x - self.size/2 - outline_offset, 
                         self.y - self.size/2 - outline_offset, 
                         self.size + 2*outline_offset, 
                         self.size + 2*outline_offset))  # Outline
        pygame.draw.rect(screen, constants.GREEN, 
                        (self.x - self.size/2, 
                         self.y - self.size/2, 
                         self.size, 
                         self.size))
        
        # Calculate the player's visual center
        center_x = self.x
        center_y = self.y
        
        # Direction arrow
        arc_radius = self.size      # Distance from the center where the line starts
        arrow_length = self.size/2    # Length of the line beyond that point
        angle_rad = math.radians(self.angle)
        
        # Starting point: on the circle (arc) boundary relative to the player's center
        start_line_x = center_x + arc_radius * math.cos(angle_rad)
        start_line_y = center_y + arc_radius * math.sin(angle_rad)
        
        # End point: further out by arrow_length pixels
        end_line_x = center_x + (arc_radius + arrow_length) * math.cos(angle_rad)
        end_line_y = center_y + (arc_radius + arrow_length) * math.sin(angle_rad)
        
        pygame.draw.line(screen, constants.BLUE,
                        (start_line_x, start_line_y),
                        (end_line_x, end_line_y), 3)
        
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

        # Restrict player to screen boundaries with size consideration (10 pixel xp bar)
        half_size = self.size/2
        self.x = max(half_size, min(new_x, self.screen_width - half_size - 10))
        self.y = max(half_size, min(new_y, self.screen_height - half_size - 10))

    def update_hp_regen(self):
        self.ticks_since_last_hp_regen += 1
        if self.ticks_since_last_hp_regen >= constants.FPS:
            regen_amount = (self.max_health * (self.hp_regen + self.hp_regen_percent_bonus) / 100)
            self.heal(regen_amount)
            self.ticks_since_last_hp_regen = 0
    
    def update(self, keys):
        if self.state == PlayerState.DEAD:
            return
        self.current_tick += 1  # Increment tick counter
        self.update_hp_regen()
        self.update_buffs()
        self.move(keys)

        # Handle shield regeneration
        if not self.barrier_shield_active and self.barrier_shield_hp <= 0:
            if self.barrier_shield_regeneration_time > 0:
                self.barrier_shield_regeneration_time -= 1
                print(f"Shield regeneration timer: {self.barrier_shield_regeneration_time}")
            else:
                self.barrier_shield_hp = self.max_health * constants.BARRIER_SHIELD_HP_FRACTION
                self.barrier_shield_active = True
                print("Shield regenerated and is now active.")

    def update_buffs(self):
        # Remove expired buffs
        self.active_buffs = [buff for buff in self.active_buffs if buff["end_tick"] > self.current_tick]

    def add_temporary_buff(self, buff_name, duration_seconds):
        # Convert duration from seconds to ticks (60 ticks = 1 second)
        duration_ticks = duration_seconds * constants.FPS
        buff = {
            "name": buff_name,
            "end_tick": self.current_tick + duration_ticks
        }
        if not hasattr(self, 'active_buffs'):
            self.active_buffs = []
        self.active_buffs.append(buff)

    def has_active_buff(self, buff_name):
        return any(buff["name"] == buff_name for buff in self.active_buffs)

    @property
    def effective_damage_multiplier(self):
        # Import game_state locally to avoid potential circular dependencies.
        import src.game_state as game_state
        # For each enemy on screen, add 20% extra damage.
        enemy_bonus = 1 + self.rage_percent_bonus/100 * len(game_state.enemies)
        projectile_bonus = 1 + self.frenzy_percent_bonus/100 * len(game_state.projectiles)
        fear_bonus = 1 + self.fear_percent_bonus/100 * (self.max_health - self.health) / self.max_health
        
        # Add heart pickup damage boost - stacks exponentially
        buff_multiplier = (1 + self.hp_pickup_damage_boost_percent_bonus/100)
        active_buff_count = sum(1 for buff in self.active_buffs if buff["name"] == "heart_damage_boost")
        buff_bonus = buff_multiplier ** active_buff_count
        
        return self.base_damage_multiplier * enemy_bonus * projectile_bonus * fear_bonus * buff_bonus

    def shoot_regular(self, mouse_pos):
        import src.game_state as game_state
        # Check if the player is dead or the cooldown (in ticks) has not elapsed
        if self.state == PlayerState.DEAD or (game_state.in_game_ticks_elapsed - self.last_shot_time) < (self.shoot_cooldown * constants.FPS):
            return None

        mx, my = mouse_pos
        angle = calculate_angle(self.x, self.y, mx, my)
        # Update last shot tick to current tick count
        self.last_shot_time = game_state.in_game_ticks_elapsed

        bullets = []
        total_projectiles = 1 + self.basic_bullet_extra_projectiles_per_shot_bonus
        effective_multiplier = self.effective_damage_multiplier

        if total_projectiles == 1:
            bullets.append(PlayerBasicBullet(
                self.x, self.y, angle, 
                effective_multiplier,
                self.basic_bullet_damage_multiplier, 
                self.basic_bullet_speed_multiplier, 
                math.ceil(self.basic_bullet_piercing_multiplier)
            ))
            return bullets

        # For multiple projectiles, space them out perpendicular to the shooting direction
        spread_distance = 15  # pixels between projectiles
        perpendicular_angle = angle + 90  # perpendicular direction in degrees
        total_spread = spread_distance * (total_projectiles - 1)
        start_x = self.x - (total_spread / 2) * math.cos(math.radians(perpendicular_angle))
        start_y = self.y - (total_spread / 2) * math.sin(math.radians(perpendicular_angle))
        
        for i in range(total_projectiles):
            offset_x = start_x + (spread_distance * i) * math.cos(math.radians(perpendicular_angle))
            offset_y = start_y + (spread_distance * i) * math.sin(math.radians(perpendicular_angle))
            bullets.append(PlayerBasicBullet(
                offset_x, offset_y, angle,
                effective_multiplier,
                self.basic_bullet_damage_multiplier,
                self.basic_bullet_speed_multiplier,
                self.basic_bullet_piercing_multiplier
            ))
        
        return bullets

    def shoot_special(self, mouse_pos):
        import src.game_state as game_state
        # Check if the player is dead or the special cooldown (in ticks) has not elapsed
        if self.state == PlayerState.DEAD or (game_state.in_game_ticks_elapsed - self.last_special_shot_time) < (self.special_shot_cooldown * constants.FPS):
            return None

        mx, my = mouse_pos
        angle = calculate_angle(self.x, self.y, mx, my)
        # Update last special shot tick to current tick count
        self.last_special_shot_time = game_state.in_game_ticks_elapsed

        effective_multiplier = self.effective_damage_multiplier
        return [PlayerSpecialBullet(
            self.x, self.y, angle,
            effective_multiplier,
            self.special_bullet_damage_multiplier,
            self.special_bullet_speed_multiplier,
            self.special_bullet_piercing_multiplier,
            self.special_bullet_radius_multiplier,
            self.special_bullet_can_repierce
        )]

    def take_damage(self, amount):
        if self.barrier_shield_active and self.barrier_shield_hp > 0:
            absorbed_damage = min(amount, self.barrier_shield_hp)
            self.barrier_shield_hp -= absorbed_damage
            remaining_damage = amount - absorbed_damage

            print(f"Shield absorbed {absorbed_damage} damage. Remaining shield HP: {self.barrier_shield_hp}")

            if self.barrier_shield_hp <= 0:
                self.barrier_shield_active = False
                self.barrier_shield_regeneration_time = constants.BARRIER_SHIELD_REGENERATION_TIME  # Start regeneration timer
                print("Shield depleted. Regeneration started.")

            if remaining_damage > 0:
                self.health -= remaining_damage
                print(f"Health reduced by {remaining_damage}. Current health: {self.health}")
                if self.health <= 0:
                    self.state = PlayerState.DEAD
                    print("Player has died.")
        else:
            self.health -= amount
            print(f"Health reduced by {amount}. Current health: {self.health}")
            if self.health <= 0:
                self.state = PlayerState.DEAD
                print("Player has died.")

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def heal_from_pickup(self):
        heal_amount = self.max_health * ((self.hp_pickup_healing_percent_bonus+constants.base_hp_pickup_healing_percent) / 100)
        self.heal(heal_amount)
        self.add_temporary_buff("heart_damage_boost", self.hp_pickup_damage_boost_duration_s)  # 30 second damage boost
        self.base_damage_multiplier = self.base_damage_multiplier * (1 + self.hp_pickup_permanent_damage_boost_percent_bonus/100)
        self.max_health = self.max_health * (1 + self.hp_pickup_permanent_hp_boost_percent_bonus/100)
        return heal_amount
        

    def get_cooldown_progress(self):
        import src.game_state as game_state
        current_tick = game_state.in_game_ticks_elapsed
        regular_progress = (current_tick - self.last_shot_time) / (self.shoot_cooldown * constants.FPS)
        special_progress = (current_tick - self.last_special_shot_time) / (self.special_shot_cooldown * constants.FPS)
        # Clamp the progress values so that they do not exceed 1.0
        return min(1, regular_progress), min(1, special_progress)
    
    def gain_experience(self, amount):
        # Apply XP gain bonus as a percentage increase
        import src.game_state as game_state
        bonus_multiplier = 1 + (self.xp_gain_percent_bonus / 100)
        modified_amount = amount * bonus_multiplier
        self.player_experience += modified_amount
        if self.player_experience >= self.experience_to_next_level:
            self.level_up()
        game_state.experience_updates.append({
            "x": self.x,
            "y": self.y,
            "value": int(modified_amount),
            "timer": 60,
            "color": constants.BLUE
        })
            
    def level_up(self):
        self.player_level += 1
        self.player_experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * constants.level_up_xp_cost_scaling_factor)
        self.state = PlayerState.LEVELING_UP
        print(f"Player leveled up to level {self.player_level}")
            

    def apply_upgrade(self, upgrade):
        upgrade.apply(self)
        self.upgrade_levels[upgrade.name] = self.upgrade_levels.get(upgrade.name, 0) + 1
        self.applied_upgrades.add(upgrade.name)  # Store upgrade names as strings
        print(f"Applied upgrade: {upgrade.name}")  # Debugging output
        
        # Activate the shield if the Barrier Shield upgrade is applied
        if upgrade.name == "Barrier Shield":
            self.barrier_shield_active = True
            self.barrier_shield_hp = self.max_health * constants.BARRIER_SHIELD_HP_FRACTION  # Ensure HP is set
            print(f"Barrier Shield activated with HP: {self.barrier_shield_hp}")  # Debugging output

    def is_dead(self):
        return self.state == PlayerState.DEAD
