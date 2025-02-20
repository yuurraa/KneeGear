# special_effects.py
import pygame
from src.engine import game_state
from src.player.player import PlayerState

class HoshimachiProjectileSkin:
    def __init__(self, base_image, weapon_scale_factor_x=1.0, weapon_scale_factor_y=1.0, spin_speed=20):
        self.base_image = base_image
        self.current_angle = 0
        self.weapon_scale_factor_x = weapon_scale_factor_x
        self.weapon_scale_factor_y = weapon_scale_factor_y
        self.spin_speed = spin_speed  # degrees to spin per update

    def update(self):
        # Only update the spin if the game is running normally
        if (not game_state.paused and not game_state.game_over and 
            not game_state.showing_upgrades and not game_state.showing_stats and 
            game_state.player.state != PlayerState.LEVELING_UP):
            self.current_angle = (self.current_angle + self.spin_speed) % 360

    def draw(self, screen, x, y, size):
        # Scale the image
        scale_x = size * self.weapon_scale_factor_x
        scale_y = size * self.weapon_scale_factor_y
        scaled_image = pygame.transform.scale(self.base_image, (int(scale_x), int(scale_y)))
        # Rotate only based on the projectile's own spin
        rotated_image = pygame.transform.rotate(scaled_image, self.current_angle)
        # Draw it centered at (x, y)
        rect = rotated_image.get_rect(center=(x, y))
        screen.blit(rotated_image, rect.topleft)
