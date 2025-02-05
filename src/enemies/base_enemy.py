import math
import random
import constants
from helpers import calculate_angle
from projectiles import Alignment

class BaseEnemy:
    def __init__(self, x, y, scaling):
        """
        Initialize the base enemy with position and scaling.
        """
        self.x = x
        self.y = y
        self.scaling = scaling
        self.health = 100 * scaling  # Default health; override in subclasses as needed.
        self.type = "base"
    
    def update(self, target_x, target_y, current_tick, game_state):
        """
        Update the enemy by moving and then shooting.
        """
        self.move(target_x, target_y, game_state)
        self.shoot(target_x, target_y, current_tick, game_state)
    
    def move(self, target_x, target_y, game_state):
        """
        Default movement behavior. Moves the enemy toward the target using basic speed.
        """
        speed = constants.basic_enemy_speed
        angle = math.radians(calculate_angle(self.x, self.y, target_x, target_y))
        self.x += speed * math.cos(angle)
        self.y += speed * math.sin(angle)
    
    def shoot(self, target_x, target_y, current_tick, game_state):
        """
        Default shoot behavior does nothing. Subclasses should override this.
        """
        pass
