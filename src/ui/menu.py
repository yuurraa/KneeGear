import src.engine.game_state as game_state
# ACCESSED FROM MAIN.PY
from src.ui.menus.in_game_menus import draw_pause_menu, draw_level_up_menu, draw_stats_tab, draw_upgrades_tab
from src.ui.menus.main_menus import draw_main_menu, draw_skin_selection_menu

# Dynamically assign attributes to game_state to satisfy linter type checking
if not hasattr(game_state, 'pause_ui'):
    game_state.pause_ui = {}  # type: ignore
if not hasattr(game_state, 'pause_music_ui'):
    game_state.pause_music_ui = {}  # type: ignore
if not hasattr(game_state, 'song_ticker_offset'):
    game_state.song_ticker_offset = 0.0  # type: ignore
if not hasattr(game_state, 'current_upgrade_buttons'):
    game_state.current_upgrade_buttons = []  # type: ignore
if not hasattr(game_state, 'final_time'):
    game_state.final_time = 0  # type: ignore
if not hasattr(game_state, 'current_song_display'):
    game_state.current_song_display = ""  # type: ignore
if not hasattr(game_state, 'skin_buttons'):
    game_state.skin_buttons = []  # type: ignore
if not hasattr(game_state, 'close_button'):
    game_state.close_button = None  # type: ignore
