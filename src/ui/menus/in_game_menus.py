import pygame
import math

import src.engine.game_state as game_state
import src.engine.constants as constants
from src.engine.helpers import get_ui_scaling_factor, compute_shimmer_surface_for_tab_icon
from src.ui.components.ui_buttons import Button, IconButton, UpgradeButton
from src.ui.components.ui_sliders import Slider

ui_scaling_factor = get_ui_scaling_factor()

def draw_level_up_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Get the number of upgrade choices the player should have
    num_choices = 3  # Default
    if any(upgrade.name == "+1 Upgrade Choice" for upgrade in game_state.player.applied_upgrades):
        num_choices = 4

    # Create menu panel - using proportional sizes and adjusting width based on number of choices
    panel_width = int(game_state.screen_width * (0.65 if num_choices == 3 else 0.85))
    panel_height = int(game_state.screen_height * 0.4)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(4 * ui_scaling_factor))

    # Level up text
    text = game_state.FONTS["large"].render(f"Level {game_state.player.player_level} - Choose an Upgrade", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + 100 * ui_scaling_factor))
    screen.blit(text, text_rect)

    # Create buttons if they don't exist or if the list is empty
    if not getattr(game_state, 'current_upgrade_buttons', None) or not game_state.current_upgrade_buttons:
        # Get random upgrades
        from src.player.upgrades import UpgradePool
        upgrade_pool = UpgradePool()
        upgrades = upgrade_pool.get_random_upgrades(num_choices, game_state.player)
        
        # Create buttons with proportional sizes
        button_width = int(game_state.screen_width * 0.18)  # ~16% of screen width
        button_height = int(game_state.screen_height * 0.2)  # ~15% of screen height
        button_spacing = int(game_state.screen_width * 0.023)  # ~2.6% of screen width
        
        # Calculate total width of all buttons and spacing
        total_width = (button_width * num_choices) + (button_spacing * (num_choices - 1))
        start_x = (game_state.screen_width - total_width) // 2

        game_state.current_upgrade_buttons = []
        for i, upgrade in enumerate(upgrades):
            x = start_x + (button_width + button_spacing) * i
            y = panel_y + 230 * ui_scaling_factor
            icon_image = upgrade_pool.icon_images.get(upgrade.icon, None)
            button = UpgradeButton(x, y, button_width, button_height, upgrade, icon_image)
            game_state.current_upgrade_buttons.append(button)

    # Draw existing buttons
    for button in game_state.current_upgrade_buttons:
        button.update()  # Update button cooldown
        button.draw(screen)

    return (game_state.current_upgrade_buttons)

def draw_pause_menu(screen):
    # Initialize dynamic attributes on game_state if not already set
    if not hasattr(game_state, 'pause_ui'):
        game_state.pause_ui = {}
    if not hasattr(game_state, 'pause_music_ui'):
        game_state.pause_music_ui = {}
    if not hasattr(game_state, 'song_ticker_offset'):
        game_state.song_ticker_offset = 0.0

    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create menu panel with proportional sizes
    panel_width = int(game_state.screen_width * 0.6 * ui_scaling_factor)
    panel_height = int(game_state.screen_height * 0.65 * ui_scaling_factor)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(4 * ui_scaling_factor))

    # Pause menu title
    text = game_state.FONTS["large"].render("Pause Menu", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + int(80 * ui_scaling_factor)))
    screen.blit(text, text_rect)

    # Standard icon size and padding
    icon_size = int(65 * ui_scaling_factor)
    icon_padding = int(40 * ui_scaling_factor)

    # Slider dimensions (adjusted length)
    slider_width = int((panel_width - (icon_size + 5 * icon_padding) * 0.85))
    slider_height = int(game_state.screen_height * 0.02)
    slider_y = panel_y + int(150 * ui_scaling_factor)

    # --- Center the Volume Icon and Slider as a Group ---
    total_volume_width = icon_size + icon_padding + slider_width
    group_start_x = panel_x + (panel_width - total_volume_width) // 2
    volume_icon_x = group_start_x + 20 * ui_scaling_factor
    slider_x = group_start_x + icon_size + icon_padding

    music_bar_y = slider_y + int(65 * ui_scaling_factor)
    buttons_y = music_bar_y + int(120 * ui_scaling_factor)

    # Initialize UI elements if not already created
    if not hasattr(game_state, 'pause_ui') or not game_state.pause_ui:
        button_width = int(game_state.screen_width * 0.104)
        button_height = int(game_state.screen_height * 0.056)
        button_x = (game_state.screen_width - (button_width * 2 + int(game_state.screen_width * 0.01))) // 2
        buttons_spacing = 20 * ui_scaling_factor

        volume_slider = Slider(slider_x, slider_y, slider_width, slider_height, constants.music_volume)

        upgrades_button = Button(button_x, buttons_y, button_width, button_height, "Upgrades", constants.BLUE)
        stats_button = Button(button_x + button_width + buttons_spacing, buttons_y, button_width, button_height, "Stats", constants.ORANGE)
        resume_button = Button(button_x, buttons_y + button_height + buttons_spacing, button_width, button_height, "Resume", constants.GREEN)
        quit_button = Button(button_x + button_width + buttons_spacing, buttons_y + button_height + buttons_spacing, button_width, button_height, "Quit", constants.RED)

        game_state.pause_ui = {
            'quit_button': quit_button,
            'resume_button': resume_button,
            'volume_slider': volume_slider,
            'upgrades_button': upgrades_button,
            'stats_button': stats_button
        }

    # ---- NEW: Music Control Bar UI ----
    if not hasattr(game_state, 'pause_music_ui') or not game_state.pause_music_ui:
        music_bar_margin = 40 * ui_scaling_factor
        music_bar_width = panel_width - (int(4 * ui_scaling_factor) * music_bar_margin)
        music_bar_x = panel_x + music_bar_margin

        btn_size = icon_size

        playlist_icon = pygame.image.load("assets/ui/playlist.png").convert_alpha()
        previous_icon = pygame.image.load("assets/ui/previous.png").convert_alpha()
        next_icon = pygame.image.load("assets/ui/next.png").convert_alpha()

        playlist_icon = pygame.transform.scale(playlist_icon, (icon_size - int(4 * ui_scaling_factor), icon_size - int(4 * ui_scaling_factor)))
        previous_icon = pygame.transform.scale(previous_icon, (icon_size - 20 * ui_scaling_factor, icon_size - 20 * ui_scaling_factor))
        next_icon = pygame.transform.scale(next_icon, (icon_size - 20 * ui_scaling_factor, icon_size - 20 * ui_scaling_factor))

        playlist_button = IconButton(music_bar_x, music_bar_y, btn_size, btn_size, image=playlist_icon)
        previous_button = IconButton(music_bar_x + btn_size + 10 * ui_scaling_factor, music_bar_y, btn_size, btn_size, image=previous_icon)
        next_button = IconButton(music_bar_x + music_bar_width - btn_size + 10 * ui_scaling_factor, music_bar_y, btn_size, btn_size, image=next_icon)
        
        song_display_x = music_bar_x + (2 * btn_size + 40 * ui_scaling_factor) - 10 * ui_scaling_factor
        song_display_width = music_bar_width - (3 * btn_size + 40 * ui_scaling_factor)
        song_display_rect = pygame.Rect(song_display_x, music_bar_y, song_display_width, btn_size)
        
        game_state.pause_music_ui = {
            'playlist_button': playlist_button,
            'previous_button': previous_button,
            'next_button': next_button,
            'song_display_rect': song_display_rect
        }

    # Draw the persistent pause UI
    game_state.pause_ui['quit_button'].draw(screen)
    game_state.pause_ui['resume_button'].draw(screen)
    game_state.pause_ui['volume_slider'].draw(screen)
    game_state.pause_ui['upgrades_button'].draw(screen)
    game_state.pause_ui['stats_button'].draw(screen)

    # ---- Draw Volume Icon ----
    volume_icon = pygame.image.load("assets/ui/volume.png").convert_alpha()
    volume_icon = pygame.transform.scale(volume_icon, (icon_size - int(4 * ui_scaling_factor), icon_size - int(4 * ui_scaling_factor)))
    volume_icon_y = slider_y + (slider_height - icon_size) // 2
    screen.blit(volume_icon, (volume_icon_x, volume_icon_y))

    # ---- Draw Music Bar ----
    music_ui = game_state.pause_music_ui  # type: ignore
    music_ui['playlist_button'].draw(screen)
    music_ui['previous_button'].draw(screen)
    music_ui['next_button'].draw(screen)
    
    pygame.draw.rect(screen, constants.LIGHT_GREY, music_ui['song_display_rect'])
    pygame.draw.rect(screen, constants.BLACK, music_ui['song_display_rect'], 2)
    
    current_song_display = getattr(game_state, 'current_song_display', "No Song")
    text_surface = game_state.FONTS["small"].render(current_song_display, True, constants.BLACK)
    
    padding = 70 * ui_scaling_factor  
    ticker_width = text_surface.get_width() + padding

    display_rect = music_ui['song_display_rect']
    display_width = display_rect.width
    display_height = display_rect.height

    game_state.song_ticker_offset += 0.5  
    if game_state.song_ticker_offset >= ticker_width:
        game_state.song_ticker_offset -= ticker_width

    center_y = display_rect.y + (display_height - text_surface.get_height()) // 2

    previous_clip = screen.get_clip()
    screen.set_clip(display_rect)

    start_x = -game_state.song_ticker_offset
    while start_x < display_width:
        screen.blit(text_surface, (display_rect.x + start_x, center_y))
        start_x += ticker_width

    screen.set_clip(previous_clip)

    return (game_state.pause_ui['quit_button'],
            game_state.pause_ui['resume_button'],
            game_state.pause_ui['volume_slider'],
            game_state.pause_ui['upgrades_button'],
            game_state.pause_ui['stats_button'],
            game_state.pause_music_ui['playlist_button'],
            game_state.pause_music_ui['previous_button'],
            game_state.pause_music_ui['next_button'])

def draw_upgrades_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Constants for button dimensions
    button_width = int(game_state.screen_width * 0.25)
    button_height = int(game_state.screen_height * 0.046)
    button_spacing = int(game_state.screen_width * 0.01)  # Horizontal spacing

    # Use 75% of the screen height for the icon area
    max_column_height = int(game_state.screen_height * 0.8)
    title_height = int(game_state.screen_height * 0.037)
    close_button_height = int(game_state.screen_height * 0.046)

    # Calculate the number of upgrades
    num_upgrades = len(game_state.player.applied_upgrades)

    # Calculate total height for all buttons
    total_icon_height = (button_height * num_upgrades) + (button_spacing * (num_upgrades - 1))

    # Calculate the number of columns
    num_columns = math.ceil(total_icon_height / max_column_height) if total_icon_height > 0 else 1

    # Dynamic panel height based on the total icon height
    dynamic_panel_height = min(total_icon_height, max_column_height)
    panel_height = title_height + dynamic_panel_height + close_button_height + 120 * ui_scaling_factor

    # Calculate panel width based on the number of columns
    panel_width = num_columns * (button_width + button_spacing)

    # Center the panel
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw title
    title_surface = game_state.FONTS["medium"].render("Obtained Upgrades", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + title_height // 2 + 30 * ui_scaling_factor))
    screen.blit(title_surface, title_rect)

    # Draw upgrades
    phase = ((pygame.time.get_ticks() / 5) % 360) / 360.0
    column_width = button_width + button_spacing

    y_offset = panel_y + title_height + 60 * ui_scaling_factor  # Starting Y position
    for i, upgrade in enumerate(game_state.player.applied_upgrades):
        column_index = i % num_columns
        row_index = i // num_columns

        x_offset = panel_x + column_index * column_width + (column_width - button_width) // 2
        current_y_offset = y_offset + row_index * (button_height + button_spacing) - 20 * ui_scaling_factor

        rarity_color = UpgradeButton.RARITY_COLORS.get(upgrade.Rarity, constants.LIGHT_GREY)
        shimmer_surface = compute_shimmer_surface_for_tab_icon(rarity_color, upgrade.Rarity, button_width, button_height, phase)
        screen.blit(shimmer_surface, (x_offset, current_y_offset))

        pygame.draw.rect(screen, constants.BLACK, (x_offset, current_y_offset, button_width, button_height), int(4 * ui_scaling_factor))

        # Draw upgrade name
        display_name = f"{upgrade.name} ({game_state.player.upgrade_levels.get(upgrade.name, 0)}x)"
        name_surface = game_state.FONTS["small"].render(display_name, True, constants.BLACK)
        name_rect = name_surface.get_rect(center=(x_offset + button_width // 2, current_y_offset + button_height // 2))
        screen.blit(name_surface, name_rect)

    # Draw close button
    close_button_x = panel_x + (panel_width - 200 * ui_scaling_factor) // 2
    close_button_y = panel_y + panel_height - close_button_height - 20 * ui_scaling_factor
    close_button = Button(close_button_x, close_button_y, 200 * ui_scaling_factor, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (close_button)

def draw_stats_tab(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Panel dimensions and positioning
    panel_width = int(game_state.screen_width * 0.6)
    panel_height = int(game_state.screen_height * 0.75)
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2

    # Draw the panel background and border
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), int(4 * ui_scaling_factor))

    # Draw title at the top
    title_surface = game_state.FONTS["medium"].render("Player Stats", True, constants.BLACK)
    title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, panel_y + 60 * ui_scaling_factor))
    screen.blit(title_surface, title_rect)

    # Define groups of stats with headers
    groups = [
        ("Basic Stats", [
            ("Level", f"{game_state.player.player_level:.1f}"),
            ("Experience", f"{game_state.player.player_experience:.1f}"),
            ("XP Gain Multiplier", f"{game_state.player.xp_gain_multiplier:.1f}"),
            ("Passive XP Gain (%)", f"{game_state.player.passive_xp_gain_percent_bonus:.1f}"),
            ("Speed", f"{game_state.player.speed:.1f}"),
            ("Damage Reduction (%)", f"{game_state.player.damage_reduction_percent_bonus:.1f}"),
        ]),
        ("Health Stats", [
            ("Health", f"{game_state.player.health:.1f}"),
            ("Max Health", f"{game_state.player.max_health:.1f}"),
            ("Health Regen (%)", f"{game_state.player.hp_regen:.1f}"),
            ("Health Regen Bonus (%)", f"{game_state.player.hp_regen_percent_bonus:.1f}"),
            ("Lifesteal (%)", f"{game_state.player.hp_steal:.1f}"),
        ]),
        ("Basic Bullet Stats", [
            ("Damage Multiplier", f"{game_state.player.base_damage_multiplier:.1f}"),
            ("Basic Bullet Damage Multiplier", f"{game_state.player.basic_bullet_damage_multiplier:.1f}"),
            ("Basic Bullet Speed Multiplier", f"{game_state.player.basic_bullet_speed_multiplier:.1f}"),
            ("Basic Bullet Piercing Multiplier", f"{game_state.player.basic_bullet_piercing_multiplier:.1f}"),
            ("Basic Bullet Cooldown (s)", f"{game_state.player.shoot_cooldown:.1f}"),
            ("Basic Bullet Scales w/ Distance", f"{game_state.player.basic_bullet_scales_with_distance_travelled:.1f}"),
            ("Extra Projs/Shot", f"{game_state.player.basic_bullet_extra_projectiles_per_shot_bonus:.1f}"),
        ]),
        ("Random", [
            ("Roll the Dice Chance (%)", f"{game_state.player.random_upgrade_chance * 100:.1f}"),
        ]),
        ("Special Bullet Stats", [
            ("Special Bullet Damage Multiplier", f"{game_state.player.special_bullet_damage_multiplier:.1f}"),
            ("Special Bullet Speed Multiplier", f"{game_state.player.special_bullet_speed_multiplier:.1f}"),
            ("Special Bullet Piercing Multiplier", f"{game_state.player.special_bullet_piercing_multiplier:.1f}"),
            ("Special Bullet Radius Multiplier", f"{game_state.player.special_bullet_radius_multiplier:.1f}"),
            ("Special Bullet Cooldown (s)", f"{game_state.player.special_shot_cooldown:.1f}"),
            ("Special Bullet Can Repierce", f"{game_state.player.special_bullet_can_repierce:.1f}"),
            ("Special Bullet Scales w/ Dist", f"{game_state.player.special_bullet_scales_with_distance_travelled:.1f}"),
        ]),
        ("Pickup Stats", [
            ("Maximum Pickups", f"{game_state.player.max_pickups_on_screen:.1f}"),
            ("Pickup Heal Bonus (%)", f"{game_state.player.hp_pickup_healing_percent_bonus:.1f}"),
            ("Pickup Temp Damage Boost Duration (s)", f"{game_state.player.hp_pickup_damage_boost_duration_s:.1f}"),
            ("Pickup Temp Damage Boost (%)", f"{game_state.player.hp_pickup_damage_boost_percent_bonus:.1f}"),
            ("Pickup Permanent Health Boost (%)", f"{game_state.player.hp_pickup_permanent_hp_boost_percent_bonus:.1f}"),
            ("Pickup Permanent Damage Boost (%)", f"{game_state.player.hp_pickup_permanent_damage_boost_percent_bonus:.1f}"),
        ]),
        ("Special Bonus Stats", [
            ("Vengeful Special Bullet Dmg Bonus (%)", f"{game_state.player.percent_damage_taken_special_attack_bonus:.1f}"),
            ("Rage Bonus (%)", f"{game_state.player.rage_percent_bonus:.1f}"),
            ("Frenzy Bonus (%)", f"{game_state.player.frenzy_percent_bonus:.1f}"),
            ("Fear Bonus (%)", f"{game_state.player.fear_percent_bonus:.1f}"),
            ("Pride (No Damage Buff Req) (s)", f"{game_state.player.no_damage_buff_req_duration:.1f}"),
            ("Pride (No Damage Buff Mult)", f"{game_state.player.no_damage_buff_damage_bonus_multiplier:.1f}"),
        ]),
    ]

    # Spacing and margin settings
    top_margin = panel_y + 140 * ui_scaling_factor  # space reserved at top (below title)
    bottom_margin = 40 * ui_scaling_factor         # bottom margin before close button area
    left_margin = panel_x + 40 * ui_scaling_factor
    column_spacing = 30 * ui_scaling_factor

    # Calculate the maximum available vertical space for the columns
    available_height = panel_y + panel_height - bottom_margin - top_margin

    # First, compute each group's height (header + each stat + intra-group spacing)
    group_heights = []
    group_spacing = 30 * ui_scaling_factor  # extra space after each group
    for header, stat_list in groups:
        # header height plus a small gap
        h = game_state.FONTS["stat-header"].get_linesize() + 30 * ui_scaling_factor
        # add each stat line height plus a small gap
        for _name, _value in stat_list:
            h += game_state.FONTS["stat-desc"].get_linesize() + 10 * ui_scaling_factor
        # add extra spacing after the group
        h += group_spacing
        group_heights.append(h)

    # Now, greedily distribute groups into columns so that the total height in each column <= available_height
    columns = []   # each column is a list of group indices
    current_column = []
    current_height = 0

    for i, group_h in enumerate(group_heights):
        if current_height + group_h > available_height and current_column:
            # Start a new column if this group doesn't fit in the current column
            columns.append(current_column)
            current_column = [i]
            current_height = group_h
        else:
            current_column.append(i)
            current_height += group_h
    if current_column:
        columns.append(current_column)

    # Determine column width (distribute available width evenly)
    available_width = panel_width - 80 * ui_scaling_factor  # leaving some left/right margins
    num_columns = len(columns)
    column_width = (available_width - (num_columns - 1) * column_spacing) // num_columns

    # Draw the groups in each column
    for col_index, group_indices in enumerate(columns):
        # X position for this column
        col_x = left_margin + col_index * (column_width + column_spacing)
        current_y = top_margin  # start at the top margin for each column

        for i in group_indices:
            header, stat_list = groups[i]
            # Render header
            header_surface = game_state.FONTS["stat-header"].render(header, True, constants.BLACK)
            screen.blit(header_surface, (col_x, current_y))
            current_y += game_state.FONTS["stat-header"].get_linesize() + int(4 * ui_scaling_factor)

            # Render each stat line (indented slightly)
            for name, value in stat_list:
                stat_text = f"{name}: {value}"
                stat_surface = game_state.FONTS["stat-desc"].render(stat_text, True, constants.BLACK)
                screen.blit(stat_surface, (col_x + 20 * ui_scaling_factor, current_y))
                current_y += game_state.FONTS["stat-desc"].get_linesize() + 10 * ui_scaling_factor

            # Extra space after group
            current_y += group_spacing

    # Draw the close button at the bottom center of the panel
    close_button_width = 200 * ui_scaling_factor
    close_button_height = int(game_state.screen_height * 0.046)
    close_button_x = panel_x + (panel_width - close_button_width) // 2
    close_button_y = panel_y + panel_height - close_button_height - 40 * ui_scaling_factor
    close_button = Button(close_button_x, close_button_y, close_button_width, close_button_height, "Close", constants.RED)
    close_button.draw(screen)

    return (close_button)