import src.engine.constants as constants

experience_updates = []
start_time_ms = 0
in_game_ticks_elapsed = 0 #doesnt include menus
elapsed_time = 0.0

notification_queue = []  # List to hold notification dicts.
notification_message = ""
notification_timer = 126  # Timer for how long the notification should be displayed
notification_visible = False  # Flag to check if the notification is visible

# New attributes for notification animation
notification_total_duration = 126  # Total frames (0.5s in, 2s visible, 0.3s out at 60 FPS)
notification_slide_in_duration = 18    # Frames for sliding in (0.3 seconds)
notification_visible_duration = 90    # Frames for being fully visible (1.5 seconds)
notification_slide_out_duration = 18   # Frames for sliding out (0.3 seconds)
notification_current_y = -60           # Initial Y position (above the screen)

last_special_shot_time = 0
last_shot_time = 0

enemies = []
hearts = []
projectiles = []  # Will contain all bullets regardless of alignment
enemy_scaling = 1.05

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
showing_upgrades = False
showing_stats = False

game_over = False
running = True
in_main_menu = True
quit = False
first_enemy_spawned = False
pause_background = None

# Screen-related (filled in after pygame.init in main.py)
screen_width = 1920
screen_height = 1080
screen = None
dummy_surface = None
design_width = 3840
design_height = 2160

damage_numbers = []

#type def to not get type warnings
from src.player.player import Player
player:Player = None  # Will be initialized in main.py after screen dimensions are known

from src.engine.projectiles import BulletPool
bullet_pool = BulletPool()

scroll_offset = 0  # Initialize scroll offset for upgrades tab

# Add this line to define the new game state
skin_menu = False  # Flag to indicate if the skin selection menu is active

import pygame
from src.engine.helpers import get_text_scaling_factor
font_path = "assets/fonts/SourceHanSansHW-VF.ttf.ttc"

if not pygame.font.get_init():
    pygame.font.init()
FONTS = {
    'massive': pygame.font.Font(font_path, get_text_scaling_factor(120)),
    'huge': pygame.font.Font(font_path, get_text_scaling_factor(72)),
    'large': pygame.font.Font(font_path, get_text_scaling_factor(48)),
    'medium': pygame.font.Font(font_path, get_text_scaling_factor(36)),
    'stat-header': pygame.font.Font(font_path, get_text_scaling_factor(26)),
    'small': pygame.font.Font(font_path, get_text_scaling_factor(24)),
    'stat-desc': pygame.font.Font(font_path, get_text_scaling_factor(21)),
    'smaller': pygame.font.Font(font_path, get_text_scaling_factor(20)),
    'tiny': pygame.font.Font(font_path, get_text_scaling_factor(18)),
    # Add more as needed
}
FONTS['stat-header'].set_underline(True)
