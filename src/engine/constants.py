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
ORANGE = (255, 165, 0)
TRANSLUCENT_GREEN = (0, 255, 0, 128)
TRANSLUCENT_RED = (255, 0, 0, 128)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (120, 120, 120)
DARKER_GREY = (50, 50, 50)
BROWN = (139, 69, 19)

music_volume = 0.1
music_path = "assets/audio/music.mp3"

# Speeds, angles, and cooldowns
base_player_health = 110
base_player_hp_regen_percent = 0.5
player_speed = 9
player_size = 65
player_basic_bullet_speed = 40
player_basic_bullet_damage = 11
player_basic_bullet_size = 16
player_basic_bullet_pierce = 1
player_basic_bullet_cooldown = 1

player_special_bullet_speed = 58
player_special_bullet_damage = 37
player_special_bullet_size = 48
player_special_bullet_pierce = 2
player_special_bullet_cooldown = 10

player_damage_reduction_percent_cap = 97 # if damage reduction is greater than this, it will max out at 97%
base_hp_pickup_healing_percent = 15  # Will heal 15% of max health
initial_experience_to_next_level = 20
level_up_xp_cost_scaling_factor = 1.54

enemy_stat_doubling_time = 80 # seconds

base_tank_health = 110
base_tank_damage = 3
base_tank_xp_reward = 26

tank_speed = 8
tank_shotgun_interval = 4
tank_shotgun_spread = 20
tank_shotgun_bullet_count = 22
tank_bullet_speed_range = (28, 40)
tank_bullet_size = 12

base_enemy_bullet_size = 16

base_basic_enemy_health = 24
base_basic_enemy_damage = 4
base_basic_enemy_xp_reward = 15

basic_enemy_speed = 12
basic_enemy_homing_bullet_speed = 32
basic_enemy_bullet_speed = 24
basic_enemy_homing_interval = 1.2
basic_enemy_bullet_interval = 5
basic_enemy_bullet_max_turn_angle = 1.7

# Spawn intervals
base_wave_interval = 30
wave_spawn_rate_doubling_time_seconds = 300

# Add this with the other constants
experience_bar_height = 15  # Match the height used in draw_experience_bar

# Sniper Enemy Constants
base_sniper_health = 18         # Base health for a sniper enemy (scaled by enemy scaling)
base_sniper_xp_reward = 16      # XP reward when a sniper enemy is defeated
sniper_volley_interval = 3.5      # Seconds between sniper volleys
sniper_shot_delay = 0.04         # Seconds between shots in a volley
sniper_bullet_speed = 95        # Speed of sniper bullet (very fast)
sniper_bullet_damage = 12       # High damage per sniper bullet
sniper_bullet_spread = 0.5   # sniper bullet spread in radians
sniper_keep_distance = 1000             # If player is closer than this, retreat.
sniper_approach_distance = 1300         # If player is farther than this, approach.
sniper_strafe_duration = 60            # Duration (in ticks) before choosing a new strafe angle.
sniper_strafe_retreat_factor = 0.6     # Additional movement away from the player during strafing.
sniper_move_speed = 5                # Base movement speed.      
sniper_retreat_multiplier = 2.5        # Multiplier for retreat speed when player is too close.

# Charger Enemy Constants
base_charger_health = 45        # Moderate health since it's a kamikaze-style enemy
base_charger_xp_reward = 23     # Good reward since it's risky to deal with
CHARGER_ACCELERATION = 0.7      # Gradual acceleration for some challenge
CHARGER_MAX_SPEED = 38        # Fast max speed since charging is its main threat
CHARGER_NORMAL_SPEED = 18
CHARGER_BASE_DAMAGE = 10
CHARGER_MAX_HP_DAMAGE = 0.15

# Enemy drawing constants
REGULAR_ENEMY_OUTLINE_SIZE = 64
REGULAR_ENEMY_INNER_SIZE = 60
REGULAR_ENEMY_OUTLINE_COLOR = BLACK
REGULAR_ENEMY_INNER_COLOR = RED

TANK_ENEMY_OUTLINE_SIZE = 88
TANK_ENEMY_INNER_SIZE = 80
TANK_ENEMY_OUTLINE_COLOR = BLACK
TANK_ENEMY_INNER_COLOR = BROWN

SNIPER_ENEMY_OUTLINE_SIZE = 68  # Adjust as needed
SNIPER_ENEMY_INNER_SIZE = 60
SNIPER_ENEMY_OUTLINE_COLOR = BLACK
SNIPER_ENEMY_INNER_COLOR = PURPLE


# Charger appearance
CHARGER_ENEMY_OUTLINE_SIZE = 64  # Slightly smaller than regular enemies
CHARGER_ENEMY_INNER_SIZE = 56
CHARGER_ENEMY_OUTLINE_COLOR = BLACK
CHARGER_ENEMY_INNER_COLOR = PINK  # Makes it distinct from other enemies
