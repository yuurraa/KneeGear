from enum import Enum
import pygame
import math
import random

from src.projectiles import PlayerBasicBullet, PlayerSpecialBullet
from src.helpers import calculate_angle
import src.constants as constants

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

        self.dying = False
        self.death_timer = 30  # Timer for death animation (in ticks)
        
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
        self.last_damage_tick = 0  # New: Track the tick when damage was last taken
        
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
        self.basic_bullet_scales_with_distance_travelled = False
        self.special_bullet_scales_with_distance_travelled = False
        self.damage_reduction_percent_bonus = 0
        self.hp_steal = 0
        self.percent_damage_taken_special_attack_bonus = 0

        self.xp_gain_multiplier = 1
        self.passive_xp_gain_percent_bonus = 0 #percent of xp bar per second
        self.rage_percent_bonus = 0 # percent damage gain per enemy on screen
        self.frenzy_percent_bonus = 0 # percent damage gain per projectile on screen
        self.fear_percent_bonus = 0 # max percent damage gain based on how low your hp is
        self.no_damage_buff_req_duration = 0 # seconds that player must go without taking damage to activate no damage buff
        self.no_damage_buff_damage_bonus_multiplier = 0

        self.state = PlayerState.ALIVE
        
        # Shooting cooldowns
        self.shoot_cooldown = constants.player_basic_bullet_cooldown  # Regular shot cooldown in seconds
        self.special_shot_cooldown = constants.player_special_bullet_cooldown  # Special shot cooldown in seconds
        self.last_shot_time = 0
        self.last_special_shot_time = 0

        self.applied_upgrades = set()  # Tracks names of applied upgrades
        self.upgrade_levels = {}  # Tracks number of times each upgrade has been applied
        self.active_buffs = {}  # Dictionary to store active buffs and their end ticks (not times)
        
        # NEW: initialize bonus damage accumulation for the next special attack.
        self.special_attack_bonus_damage = 0
        
        # NEW: Initialize random upgrade chance
        self.random_upgrade_chance = 0.0  # Default chance
    
    def draw(self, screen):
        import random
        import pygame

        def dissolve_surface(surface, death_progress):
            """
            Returns a new surface where a fraction of the pixels (determined by death_progress)
            have been set fully transparent. death_progress should be between 0 (no dissolve)
            and 1 (fully dissolved).
            """
            new_surface = surface.copy()
            new_surface = new_surface.convert_alpha()

            width, height = new_surface.get_size()
            for x in range(width):
                for y in range(height):
                    if random.random() < death_progress:
                        new_surface.set_at((x, y), (0, 0, 0, 0))  # Fully transparent pixel
            return new_surface

        # Check if the player is in a "dying" state
        max_death_timer = 60  # Example: 60 ticks for the death animation
        death_progress = 0.0  # No dissolve by default
        alpha = 255  # Full opacity by default

        if self.dying:  # Assuming self.dying is a boolean property
            death_progress = (max_death_timer - self.death_timer) / max_death_timer
            alpha = int(255 * (1 - death_progress))

        # Create the player body with per-pixel alpha
        body_surface = pygame.Surface((self.size + 2, self.size + 2), pygame.SRCALPHA)
        body_inner_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # Fill the outline and body colors
        body_surface.fill((*constants.BLACK, alpha))
        body_inner_surface.fill((*constants.GREEN, alpha))

        # If the player is dying, apply the dissolve effect
        if self.dying:
            body_surface = dissolve_surface(body_surface, death_progress)
            body_inner_surface = dissolve_surface(body_inner_surface, death_progress)

        # Blit the body (outline and inner rectangle)
        screen.blit(body_surface, (self.x - self.size / 2 - 1, self.y - self.size / 2 - 1))
        screen.blit(body_inner_surface, (self.x - self.size / 2, self.y - self.size / 2))

        # Direction arrow
        if not self.dying:  # Optionally, you can hide the arrow during the dissolve
            outline_offset = 1
            arc_radius = self.size  # Distance from the center where the line starts
            arrow_length = self.size / 2  # Length of the line beyond that point
            angle_rad = math.radians(self.angle)

            # Starting point: on the circle (arc) boundary relative to the player's center
            start_line_x = self.x + arc_radius * math.cos(angle_rad)
            start_line_y = self.y + arc_radius * math.sin(angle_rad)

            # End point: further out by arrow_length pixels
            end_line_x = self.x + (arc_radius + arrow_length) * math.cos(angle_rad)
            end_line_y = self.y + (arc_radius + arrow_length) * math.sin(angle_rad)

            pygame.draw.line(screen, constants.BLUE,
                            (start_line_x, start_line_y),
                            (end_line_x, end_line_y), 3)

        # Draw health bar with fade effect during death
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
        self.update_passive_xp_gain()  # Apply passive XP gain each second

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
        
        # New: Increase base damage by +200% (total 3x) if no damage has been taken for 10 seconds.
        no_damage_multiplier = 1
        if self.current_tick - self.last_damage_tick >= self.no_damage_buff_req_duration * constants.FPS:
            no_damage_multiplier = 1 + self.no_damage_buff_damage_bonus_multiplier
        
        return self.base_damage_multiplier * enemy_bonus * projectile_bonus * fear_bonus * buff_bonus * no_damage_multiplier

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
                math.ceil(self.basic_bullet_piercing_multiplier),
                scales_with_distance_travelled=self.basic_bullet_scales_with_distance_travelled
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
                math.ceil(self.basic_bullet_piercing_multiplier),
                scales_with_distance_travelled=self.basic_bullet_scales_with_distance_travelled
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
            self.special_attack_bonus_damage,
            self.special_bullet_speed_multiplier,
            self.special_bullet_piercing_multiplier,
            self.special_bullet_radius_multiplier,
            can_repierce=self.special_bullet_can_repierce,
            scales_with_distance_travelled=self.special_bullet_scales_with_distance_travelled
        )]

    def take_damage(self, amount):
        import src.game_state as game_state
        # New: Reset the damage bonus timer because the player just took damage.
        self.last_damage_tick = self.current_tick
        
        capped_damage_reduction_percent = min(self.damage_reduction_percent_bonus, constants.player_damage_reduction_percent_cap)
        # Apply damage reduction (as a percentage)
        reduced_damage = amount * (1 - (capped_damage_reduction_percent / 100))
        self.health = max(0, self.health - reduced_damage)
        if self.health <= 0:
            self.state = PlayerState.DEAD
        self.special_attack_bonus_damage += amount * (self.percent_damage_taken_special_attack_bonus/100)
        
        game_state.damage_numbers.append({
                "x": game_state.player.x,
                "y": game_state.player.y,
                "value": reduced_damage,
                "timer": 60,
                "color": constants.RED
        })

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
        modified_amount = amount * self.xp_gain_multiplier
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

    def gain_random_upgrade(self):
        import src.game_state as game_state
        from src.upgrades import UpgradePool
        upgrade_pool = UpgradePool()
        upgrades = upgrade_pool.get_random_upgrades(1, self)
        
        if upgrades:
            random_upgrade = upgrades[0]
            self.apply_upgrade(random_upgrade, source="random")
            self.random_upgrade_chance = 0.02
            
            # Notification is already handled in apply_upgrade with source="random"
            print(f"Gained random upgrade: {random_upgrade.name}")  # Debugging output

    def apply_upgrade(self, upgrade, source="manual"):
        upgrade.apply(self)
        # Increment the upgrade level
        self.upgrade_levels[upgrade.name] = self.upgrade_levels.get(upgrade.name, 0) + 1
        self.applied_upgrades.add(upgrade)
        print(f"Applied upgrade: {upgrade.name}")  # Debugging output
        
        # Set notification message based on the source
        import src.game_state as game_state
        if source == "random":
            game_state.notification_message = f"Random upgrade obtained: {upgrade.name}!"
        else:
            game_state.notification_message = f"Roll the Dice chances increases to {self.random_upgrade_chance * 100}%!"
        
        game_state.notification_visible = True  # Make the notification visible
        game_state.notification_timer = game_state.notification_total_duration  # Reset timer
        
        # # Prevent recursive gain_random_upgrade calls
        # if upgrade.name == "Roll the Dice":
        #     # Do not perform Roll the Dice logic when the upgrade itself is Roll the Dice
        #     return
        
        # Check if "Roll the Dice" upgrade is active
        if self.random_upgrade_chance > 0:
            if random.random() < self.random_upgrade_chance:
                self.gain_random_upgrade()
                self.random_upgrade_chance = 0.02
                print(f"Roll the Dice chances resets to 2%!")
            else:
                # Double the chance for the next level-up
                self.random_upgrade_chance = min(self.random_upgrade_chance * 2, 1.0)  # Cap at 100%
                print(f"Roll the Dice chances increases to {self.random_upgrade_chance}!")

    def is_dead(self):
        return self.state == PlayerState.DEAD

    def update_passive_xp_gain(self):
        """
        Adds passive XP gain to the player once per second.
        The player gains a percentage of the current experience bar per second.
        For example, if passive_xp_gain_percent_bonus is 1, the player gains 
        1% of the XP required for the next level every second.
        """
        # Only update if there is a bonus
        if self.passive_xp_gain_percent_bonus > 0:
            # Check if a full second (i.e. constants.FPS ticks) has passed
            if self.current_tick % constants.FPS == 0:
                xp_gain = self.experience_to_next_level * (self.passive_xp_gain_percent_bonus / 100)
                self.gain_experience(xp_gain)
