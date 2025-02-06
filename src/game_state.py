import src.constants as constants
from src.player import Player

experience_updates = []
start_time_ms = 0
in_game_ticks_elapsed = 0 #doesnt include menus

notification_message = ""
notification_timer = 0  # Timer for how long the notification should be displayed
notification_visible = False  # Flag to check if the notification is visible

# New attributes for notification animation
notification_total_duration = 300  # Total frames (0.5s in, 4s visible, 0.5s out at 60 FPS)
notification_slide_in_duration = 30    # Frames for sliding in (0.5 seconds)
notification_visible_duration = 240    # Frames for being fully visible (4 seconds)
notification_slide_out_duration = 30   # Frames for sliding out (0.5 seconds)
notification_current_y = -60           # Initial Y position (above the screen)

last_special_shot_time = 0
last_shot_time = 0

enemies = []
hearts = []
projectiles = []  # Will contain all bullets regardless of alignment
enemy_scaling = 1.0

wave_interval = constants.base_wave_interval
wave_active = False
wave_enemies_spawned = 0
next_enemy_spawn_time = 0.0
last_wave_time = -999

fade_alpha = 0
is_restarting = False
restart_fade_out = False
is_fading_out = False 

paused = False
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

scroll_offset = 0  # Initialize scroll offset for upgrades tab

BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# In your main file, after you set fullscreen:
scale_x = screen_width / BASE_WIDTH
scale_y = screen_height / BASE_HEIGHT
scale = min(scale_x, scale_y)


