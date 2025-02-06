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
DARK_GREY = (80, 80, 80)
BROWN = (139, 69, 19)

music_volume = 0.1
music_path = "assets/audio/music.mp3"

# Speeds, angles, and cooldowns
base_player_health = 100
base_player_hp_regen_percent = 0.5
player_speed = 4.5
player_basic_bullet_speed = 10
player_basic_bullet_damage = 10
player_basic_bullet_size = 5
player_basic_bullet_pierce = 1
player_basic_bullet_cooldown = 1

player_special_bullet_speed = 15
player_special_bullet_damage = 40
player_special_bullet_size = 20
player_special_bullet_pierce = 2
player_special_bullet_cooldown = 10

player_damage_reduction_percent_cap = 97 # if damage reduction is greater than this, it will max out at 97%
base_hp_pickup_healing_percent = 15  # Will heal 15% of max health
initial_experience_to_next_level = 20
level_up_xp_cost_scaling_factor = 1.45

enemy_stat_doubling_time = 80 # seconds

base_tank_health = 120
base_tank_damage = 2
base_tank_xp_reward = 25
tank_speed = 1.5
tank_shotgun_interval = 4
tank_shotgun_spread = 20
tank_shotgun_pellet_count = 20
tank_pellet_speed_range = (7, 12)



base_basic_enemy_health = 25
base_basic_enemy_damage = 5
base_basic_enemy_xp_reward = 12
basic_enemy_speed = 3
basic_enemy_homing_bullet_speed = 7
basic_enemy_bullet_speed = 9
basic_enemy_homing_interval = 1
basic_enemy_bullet_interval = 5
basic_enemy_bullet_max_turn_angle = 1.6

# Spawn intervals
base_wave_interval = 30
wave_spawn_rate_doubling_time_seconds = 300

# Add this with the other constants
experience_bar_height = 10  # Match the height used in draw_experience_bar

# Sniper Enemy Constants
base_sniper_health = 20         # Base health for a sniper enemy (scaled by enemy scaling)
base_sniper_xp_reward = 12      # XP reward when a sniper enemy is defeated
sniper_volley_interval = 4      # Seconds between sniper volleys
sniper_shot_delay = 0.05         # Seconds between shots in a volley
sniper_bullet_speed = 17        # Speed of sniper bullet (very fast)
sniper_bullet_damage = 13       # High damage per sniper bullet
sniper_bullet_spread = 0.4   # sniper bullet spread in radians
sniper_keep_distance = 500             # If player is closer than this, retreat.
sniper_approach_distance = 750         # If player is farther than this, approach.
sniper_strafe_duration = 40            # Duration (in ticks) before choosing a new strafe angle.
sniper_strafe_retreat_factor = 0.5     # Additional movement away from the player during strafing.
sniper_move_speed = 1.5                # Base movement speed.      
sniper_retreat_multiplier = 2.0        # Multiplier for retreat speed when player is too close.

# Charger Enemy Constants
base_charger_health = 60        # Moderate health since it's a kamikaze-style enemy
base_charger_xp_reward = 20     # Good reward since it's risky to deal with
CHARGER_ACCELERATION = 0.8      # Gradual acceleration for some challenge
CHARGER_MAX_SPEED = 22        # Fast max speed since charging is its main threat
CHARGER_NORMAL_SPEED = 10


# Enemy drawing constants
REGULAR_ENEMY_OUTLINE_SIZE = 42
REGULAR_ENEMY_INNER_SIZE = 40
REGULAR_ENEMY_OUTLINE_COLOR = BLACK
REGULAR_ENEMY_INNER_COLOR = RED

TANK_ENEMY_OUTLINE_SIZE = 52
TANK_ENEMY_INNER_SIZE = 50
TANK_ENEMY_OUTLINE_COLOR = BLACK
TANK_ENEMY_INNER_COLOR = BROWN

SNIPER_ENEMY_OUTLINE_SIZE = 42  # Adjust as needed
SNIPER_ENEMY_INNER_SIZE = 40
SNIPER_ENEMY_OUTLINE_COLOR = BLACK
SNIPER_ENEMY_INNER_COLOR = PURPLE


# Charger appearance
CHARGER_ENEMY_OUTLINE_SIZE = 38  # Slightly smaller than regular enemies
CHARGER_ENEMY_INNER_SIZE = 36
CHARGER_ENEMY_OUTLINE_COLOR = BLACK
CHARGER_ENEMY_INNER_COLOR = PINK  # Makes it distinct from other enemies


