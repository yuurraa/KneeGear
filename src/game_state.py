import constants

player_health = 100
player_x = 0
player_y = 0
player_angle = 0

player_experience = 0
player_level = 1
experience_to_next_level = 100
experience_updates = []

last_special_shot_time = 0
last_shot_time = 0
shoot_cooldown = constants.shoot_cooldown 
special_shot_cooldown = constants.special_shot_cooldown 

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

