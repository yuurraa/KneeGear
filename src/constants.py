FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
TRANSLUCENT_GREEN = (0, 255, 0, 128)
TRANSLUCENT_RED = (255, 0, 0, 128)
LIGHT_GREY = (200, 200, 200)
BROWN = (139, 69, 19)

music_volume = 0.2
music_path = "assets/audio/music.mp3"

# Speeds, angles, and cooldowns
base_player_health = 100
base_player_hp_regen_percent = 1
player_speed = 4.5
player_basic_bullet_speed = 10
player_basic_bullet_damage = 10
player_basic_bullet_size = 5
player_basic_bullet_pierce = 1
player_basic_bullet_cooldown = 1

player_special_bullet_speed = 15
player_special_bullet_damage = 50
player_special_bullet_size = 20
player_special_bullet_pierce = 2
player_special_bullet_cooldown = 10

base_hp_pickup_healing_percent = 15  # Will heal 15% of max health
initial_experience_to_next_level = 20
level_up_xp_cost_scaling_factor = 1.35

enemy_stat_doubling_time = 80 # seconds

base_tank_health = 100
base_tank_damage = 2
base_tank_xp_reward = 30
tank_speed = 1.5
tank_shotgun_interval = 4
tank_shotgun_spread = 20
tank_shotgun_pellet_count = 20
tank_pellet_speed_range = (7, 12)



base_basic_enemy_health = 20
base_basic_enemy_damage = 5
base_basic_enemy_xp_reward = 10
basic_enemy_speed = 3
basic_enemy_homing_bullet_speed = 7
basic_enemy_bullet_speed = 9
basic_enemy_homing_interval = 1
basic_enemy_bullet_interval = 5
basic_enemy_bullet_max_turn_angle = 1.6

# Spawn intervals
base_enemy_spawn_interval = 6
enemy_spawn_rate_doubling_time_seconds = 300

# Add this with the other constants
experience_bar_height = 10  # Match the height used in draw_experience_bar


