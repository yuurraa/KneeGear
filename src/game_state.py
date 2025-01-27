player_health = 100
player_x = 0
player_y = 0
player_angle = 0

last_special_shot_time = 0
last_shot_time = 0
last_enemy_spawn_time = 0

enemies = []
hearts = []
projectiles = []
enemy_bullets = []
enemy_aoe_bullets = []
tank_pellets = []

fade_alpha = 0
game_over = False
running = True
first_enemy_spawned = False

# Screen-related (filled in after pygame.init in main.py)
screen_width = 0
screen_height = 0
screen = None

damage_numbers = []