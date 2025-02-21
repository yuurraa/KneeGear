# special_effects.py
import pygame
from src.engine import game_state
from src.player.player import PlayerState

class HoshimachiProjectileSkin:
    """
    A custom projectile skin for Hoshimachi Suisei's axe projectile.
    It spins!
    """
    def __init__(self, base_image, weapon_scale_factor_x=1.0, weapon_scale_factor_y=1.0, spin_speed=20):
        self.base_image = base_image
        self.current_angle = 0
        self.weapon_scale_factor_x = weapon_scale_factor_x
        self.weapon_scale_factor_y = weapon_scale_factor_y
        self.spin_speed = spin_speed  # degrees to spin per update

    def update(self):
        if (not game_state.paused and not game_state.game_over and 
            not game_state.showing_upgrades and not game_state.showing_stats and 
            game_state.player.state != PlayerState.LEVELING_UP):
            self.current_angle = (self.current_angle + self.spin_speed) % 360

    def draw(self, screen, x, y, size):
        scale_x = size * self.weapon_scale_factor_x
        scale_y = size * self.weapon_scale_factor_y
        scaled_image = pygame.transform.scale(self.base_image, (int(scale_x), int(scale_y)))
        rotated_image = pygame.transform.rotate(scaled_image, -self.current_angle)
        rect = rotated_image.get_rect(center=(x, y))
        screen.blit(rotated_image, rect.topleft)

    # NEW: Clone method to create an independent instance.
    def clone(self):
        new_instance = HoshimachiProjectileSkin(
            self.base_image,
            self.weapon_scale_factor_x,
            self.weapon_scale_factor_y,
            self.spin_speed
        )
        # Optionally, copy the current angle so the new projectile starts with the same rotation.
        new_instance.current_angle = self.current_angle
        return new_instance

class MumeiProjectileSkin:
    """
    A custom projectile skin for Nanashi Mumei's axe (or feather) projectile.
    """
    def __init__(self, base_image, weapon_scale_factor_x=1.0, weapon_scale_factor_y=1.0, initial_rotation=0):
        self.base_image = base_image
        self.base_rotation = initial_rotation
        self.weapon_scale_factor_x = weapon_scale_factor_x
        self.weapon_scale_factor_y = weapon_scale_factor_y
        self.current_firing_rotation = 0  # Default; will be set on clone

    def update(self):
        pass  # No animation    

    def draw(self, screen, x, y, size):
        scale_x = size * self.weapon_scale_factor_x
        scale_y = size * self.weapon_scale_factor_y
        scaled_image = pygame.transform.scale(self.base_image, (int(scale_x), int(scale_y)))
        total_rotation = self.base_rotation + self.current_firing_rotation
        rotated_image = pygame.transform.rotate(scaled_image, -total_rotation)
        rect = rotated_image.get_rect(center=(x, y))
        screen.blit(rotated_image, rect.topleft)

    def clone_with_firing_rotation(self, rotation):
        new_instance = MumeiProjectileSkin.__new__(MumeiProjectileSkin)
        new_instance.base_image = self.base_image
        new_instance.weapon_scale_factor_x = self.weapon_scale_factor_x
        new_instance.weapon_scale_factor_y = self.weapon_scale_factor_y
        new_instance.base_rotation = self.base_rotation
        new_instance.current_firing_rotation = rotation  # Lock in the firing angle here.
        return new_instance
