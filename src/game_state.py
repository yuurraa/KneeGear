import constants
from player import Player

experience_updates = []
start_time_ms = 0


last_special_shot_time = 0
last_shot_time = 0

last_enemy_spawn_time = 0

enemies = []
hearts = []
projectiles = []  # Will contain all bullets regardless of alignment
enemy_scaling = 1.0

fade_alpha = 0
game_over = False
running = True
first_enemy_spawned = False

# Screen-related (filled in after pygame.init in main.py)
screen_width = 0
screen_height = 0
screen = None

damage_numbers = []

#type def to not get type warnings
player:Player = None  # Will be initialized in main.py after screen dimensions are known