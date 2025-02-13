import time
import pygame
from mutagen import File
import threading
import os  # Import os module to check for file existence

import src.constants as constants
import src.game_state as game_state
import src.logic as logic
import src.drawing as drawing
import src.score as score
from src.player import Player, PlayerState
from src.helpers import reset_game, load_music_settings, get_design_mouse_pos, get_text_scaling_factor, fade_to_black, fade_from_black_step, load_skin_selection, save_skin_selection
from src.menu import draw_level_up_menu, draw_pause_menu, draw_upgrades_tab, draw_stats_tab, draw_main_menu, draw_skin_selection_menu
import random

def show_intro_screen(screen, screen_width, screen_height):
    # Create text surface using design resolution
    font = pygame.font.Font(None, get_text_scaling_factor(74))
    text = font.render("GOONER INC.", True, constants.WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Fade-in text on the dummy surface
    for alpha in range(0, 256, 5):
        screen.fill(constants.BLACK)
        text.set_alpha(alpha)
        screen.blit(text, text_rect)
        
        # Scale and update display
        pygame.display.flip()
        pygame.time.wait(10)
    
    # Display text for 2 seconds (you can still wait on the screen if needed)
    pygame.time.wait(2000)
    
    # Fade-out to black using an overlay on the dummy surface
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        # Draw the fade overlay onto the screen
        screen.blit(fade_surface, (0, 0))
        
        # Scale and update display
        pygame.display.flip()
        pygame.time.wait(10)


def show_game_over_screen(screen, screen_width, screen_height, alpha):
    # Create a surface with per-pixel alpha for fading
    game_over_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    # Fill with black background using the provided alpha for transparency
    game_over_surface.fill((0, 0, 0, alpha))
    
    # Render "YOU DIED" text
    large_font = pygame.font.Font(None, get_text_scaling_factor(74))
    text_large = large_font.render("YOU DIED", True, constants.WHITE)
    text_large_rect = text_large.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
    game_over_surface.blit(text_large, text_large_rect)
    
    # Render time, score, high score, and restart prompt
    small_font = pygame.font.Font(None, get_text_scaling_factor(36))
    
    # Final time (ensure it's available)
    final_time = getattr(game_state, 'final_time', 0)
    minutes = final_time // 60
    seconds = final_time % 60
    
    # Time survived
    timer_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
    timer_text_rect = timer_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
    game_over_surface.blit(timer_text, timer_text_rect)
    
    # Score
    score_text = small_font.render(f"Score: {score.score}", True, constants.WHITE)
    score_text_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
    game_over_surface.blit(score_text, score_text_rect)
    
    # High score
    high_score_text = small_font.render(f"High Score: {score.high_score}", True, constants.WHITE)
    high_score_text_rect = high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
    game_over_surface.blit(high_score_text, high_score_text_rect)
    
    # Restart prompt
    restart_text = small_font.render("Press SPACE to restart", True, constants.WHITE)
    restart_text_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    game_over_surface.blit(restart_text, restart_text_rect)
    
    # Add the version text at the bottom
    version_font = pygame.font.Font(None, get_text_scaling_factor(24))  # Smaller font size
    version_text = version_font.render("Gooner Game v0.1.3", True, constants.WHITE)
    version_text_rect = version_text.get_rect(center=(screen_width // 2, screen_height - 20))  # Position at the bottom
    game_over_surface.blit(version_text, version_text_rect)
    
    # Draw the entire game over surface onto the main screen
    screen.blit(game_over_surface, (0, 0))

def calculate_enemy_scaling(elapsed_seconds):
    # Double stats every 200 seconds
    # Using 2^(t/200) as scaling formula
    scaling_factor = 2 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor

def calculate_wave_spawn_interval(elapsed_seconds):
    # Start with base_enemy_spawn_interval and halve it every enemy_spawn_rate_doubling_time_seconds
    spawn_interval = constants.base_wave_interval * (2 ** (-elapsed_seconds / constants.wave_spawn_rate_doubling_time_seconds))
    
    # Set a minimum spawn interval to prevent enemies from spawning too quickly
    return max(0.5, spawn_interval)

def load_and_play_music():
    """
    Function to load and play music asynchronously.
    Uses Mutagen to get the duration without loading the entire sound.
    """
    try:
        # Load music volume from settings
        constants.music_volume = load_music_settings()

        # Use Mutagen to get the duration
        audio = File(constants.music_path)
        if audio is None or not hasattr(audio.info, 'length'):
            raise ValueError("Unsupported audio format or corrupted file.")
        
        duration = audio.info.length  # Duration in seconds
        print(f"Music duration: {duration} seconds")

        # Load music with pygame mixer
        pygame.mixer.music.load(constants.music_path)
        pygame.mixer.music.set_volume(constants.music_volume)

        # Calculate random start position, avoiding the last 10 seconds
        max_start = max(0, duration - 10)
        start_pos = random.uniform(0, max_start)
        print(f"Starting music at position: {start_pos} seconds")

        pygame.mixer.music.play(-1, start=start_pos)  # -1 for infinite loop

    except Exception as e:
        print(f"Error loading music: {e}")

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer

    # Set up the display first
    game_state.screen_width = pygame.display.Info().current_w
    game_state.screen_height = pygame.display.Info().current_h
    # Replace your display setup with:
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height), pygame.SCALED, pygame.FULLSCREEN
    )
    # Create the player after screen dimensions are known
    game_state.player = Player(
        game_state.screen_width // 2,
        game_state.screen_height // 2,
        game_state.screen_width,
        game_state.screen_height
    )

    # Show the intro screen
    show_intro_screen(game_state.screen, game_state.screen_width, game_state.screen_height)
    
    # Load skin selection at the start
    load_skin_selection()

    while True:
        if not pygame.font.get_init() or not pygame.mixer.get_init():
            pygame.font.init()
            pygame.mixer.init()
            
            
        # ---- MAIN MENU LOOP ----
        game_state.in_main_menu = True
        main_menu_faded_in = False
        game_state.fade_alpha = 255
        
        # Main menu event loop:
        while game_state.in_main_menu:
            game_state.screen.fill(constants.WHITE)
            start_button, quit_button, skin_button = draw_main_menu(game_state.screen)
            
            if not main_menu_faded_in:
                if game_state.fade_alpha > 0:
                    fade_from_black_step(game_state.screen, step=30)
                else:
                    main_menu_faded_in = True
                

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    design_mouse_pos = get_design_mouse_pos(event.pos)
                    if start_button.rect.collidepoint(design_mouse_pos):
                        # Fade out main menu (from white to black)
                        main_menu_faded_in = False
                        game_state.in_main_menu = False
                        game_state.running = True
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        game_state.fade_alpha = 255
                        break
                    elif skin_button.rect.collidepoint(design_mouse_pos):
                        game_state.skin_menu = True
                        game_state.in_main_menu = False
                        game_state.running = False
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        game_state.fade_alpha = 255
                        break
                    elif quit_button.rect.collidepoint(design_mouse_pos):
                        pygame.quit()
                        exit()  # Immediately exit
            pygame.display.flip()

        
        # ---- SKIN SELECTION MENU ----
        while game_state.skin_menu:
            game_state.screen.fill(constants.WHITE)
            skin_buttons, close_button = draw_skin_selection_menu(game_state.screen)
            if game_state.fade_alpha > 0:
                fade_from_black_step(game_state.screen, step=30)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    design_mouse_pos = get_design_mouse_pos(event.pos)
                    if close_button.rect.collidepoint(design_mouse_pos):
                        game_state.skin_menu = False
                        game_state.in_main_menu = True
                        game_state.running = False
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        break
                    else:
                        for i, btn in enumerate(skin_buttons):
                            if btn.rect.collidepoint(design_mouse_pos):
                                game_state.player.change_skin(i)
                                save_skin_selection()

            pygame.display.flip()

        # ---- GAME LOOP ----
        # Start playing music in a separate thread:
        music_thread = threading.Thread(target=load_and_play_music, daemon=True)
        music_thread.start()

        clock = pygame.time.Clock()
        score.reset_score()
        game_state.start_time_ms = pygame.time.get_ticks()

        # Main game loop
        game_loop_faded_in = False
        # Load volume at the start
        constants.music_volume = load_music_settings()

        while game_state.running:
            # Fill the background:
            game_state.screen.fill(constants.LIGHT_GREY)
            
            # POLL EVENTS ONCE PER FRAME:
            all_events = pygame.event.get()
            filtered_events = []
            escHandled = False  # We will mark the first ESC key as handled
            
            for event in all_events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not game_state.game_over:
                        if not escHandled:
                            # When pausing, capture a snapshot of the current screen
                            if not game_state.paused:
                                game_state.pause_background = game_state.screen.copy()
                            game_state.paused = not game_state.paused
                            game_state.showing_stats = False
                            game_state.showing_upgrades = False
                            escHandled = True
                    # Skip passing this ESC event further
                else:
                    filtered_events.append(event)
            events = filtered_events

            reset_triggered = False
            for event in events:
                if event.type == pygame.QUIT:
                    game_state.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_state.game_over:
                        if hasattr(game_state, 'final_time'):
                            delattr(game_state, 'final_time')
                        reset_game()
                        score.reset_score()
                        game_state.enemies.clear()
                        game_state.projectiles.clear()
                        game_state.hearts.clear()

                        game_state.player.x = game_state.screen_width // 2
                        game_state.player.y = game_state.screen_height // 2
                        game_state.screen.fill(constants.LIGHT_GREY)
                        game_loop_faded_in = False
                        game_state.fade_alpha = 255
                        reset_triggered = True
                        break
            if reset_triggered:
                continue

            # Process normal game input if no menus are active:
            if (not getattr(game_state, 'paused', False) and 
                game_state.player.state != PlayerState.LEVELING_UP and 
                not getattr(game_state, 'showing_upgrades', False) and 
                not getattr(game_state, 'showing_stats', False)):
                logic.handle_input()
                game_state.player.update_angle(pygame.mouse.get_pos())
                        # Draw enemies, projectiles, hearts, score and player
            
            for enemy in game_state.enemies:
                enemy.draw()

            for projectile in game_state.projectiles:
                projectile.draw(game_state.screen)

            for heart in game_state.hearts:
                pygame.draw.circle(game_state.screen, constants.PINK, (heart[0], heart[1]), 10)

            score.draw_score(game_state.screen)
            game_state.player.draw(game_state.screen)
            
            # Update enemy scaling and wave spawning based on elapsed time
            in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS
            game_state.enemy_scaling = calculate_enemy_scaling(in_game_seconds)
            game_state.wave_interval = calculate_wave_spawn_interval(in_game_seconds)

            # Draw cooldown icons and experience bar
            left_click_cooldown_progress, right_click_cooldown_progress = game_state.player.get_cooldown_progress()
            drawing.draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress)
            drawing.draw_experience_bar()
            
            # Draw stopwatch (time survived)
            elapsed_seconds = game_state.in_game_ticks_elapsed // constants.FPS
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            font = pygame.font.Font(None, get_text_scaling_factor(36))
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
            time_rect = time_text.get_rect(topright=(game_state.screen_width - 20, 20))
            bg_rect = time_rect.copy()
            bg_rect.inflate_ip(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill(constants.BLACK)
            bg_surface.set_alpha(128)
            game_state.screen.blit(bg_surface, bg_rect)
            game_state.screen.blit(time_text, time_rect)
            
            # ---- PAUSE MENU ----
            if getattr(game_state, 'paused', False):
                # Instead of re-filling with LIGHT_GREY, start with the captured snapshot.
                if hasattr(game_state, 'pause_background'):
                    pause_bg = game_state.pause_background.copy()
                else:
                    # Fallback if for some reason there's no captured image.
                    pause_bg = pygame.Surface((game_state.screen_width, game_state.screen_height))
                    pause_bg.fill(constants.BLACK)
                # Create a semi-transparent overlay to darken the background
                overlay = pygame.Surface((game_state.screen_width, game_state.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))  # Adjust alpha (here, 100) for desired darkness
                pause_bg.blit(overlay, (0, 0))
                # Blit the darkened background back to the screen.
                game_state.screen.blit(pause_bg, (0, 0))
                
                # Now draw the pause menu UI on top.
                quit_button, resume_button, volume_slider, upgrades_button, stats_button = draw_pause_menu(game_state.screen)
                for event in events:
                    volume_slider.handle_event(event)
                    quit_button.handle_event(event)
                    resume_button.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = get_design_mouse_pos(event.pos)
                        if quit_button.rect.collidepoint(design_mouse_pos):
                            if hasattr(game_state, 'final_time'):
                                delattr(game_state, 'final_time')
                            reset_game()
                            score.reset_score()
                            game_state.player.x = game_state.screen_width // 2
                            game_state.player.y = game_state.screen_height // 2
                            game_state.paused = False
                            game_state.in_main_menu = True
                            game_loop_faded_in = False
                            game_state.running = False  # Exit game loop to return to main menu
                            fade_to_black(game_state.screen, 5, 10)
                            game_state.screen.fill(constants.BLACK)
                            break
                        elif resume_button.rect.collidepoint(design_mouse_pos):
                            game_state.paused = False  # Close the pause menu
                        elif upgrades_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = True
                            game_state.paused = False
                        elif stats_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_stats = True
                            game_state.paused = False
                pygame.display.flip()
                continue  # Skip the rest of this frame

            # ---- UPGRADES TAB ----
            if getattr(game_state, 'showing_upgrades', False):
                close_button = draw_upgrades_tab(game_state.screen)
                for event in events:
                    if event.type == pygame.QUIT:
                        game_state.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state.showing_upgrades = False
                        game_state.paused = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = get_design_mouse_pos(event.pos)
                        if close_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = False
                            game_state.paused = True
                pygame.display.flip()
                continue

            # ---- STATS TAB ----
            if getattr(game_state, 'showing_stats', False):
                close_button = draw_stats_tab(game_state.screen)
                for event in events:
                    if event.type == pygame.QUIT:
                        game_state.running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state.showing_stats = False
                        game_state.paused = True
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = get_design_mouse_pos(event.pos)
                        if close_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_stats = False
                            game_state.paused = True
                pygame.display.flip()
                continue

            # ---- LEVEL-UP MENU ----
            if game_state.player.state == PlayerState.LEVELING_UP:
                upgrade_buttons = draw_level_up_menu(game_state.screen)
                for event in events:
                    if event.type == pygame.QUIT:
                        game_state.running = False
                        break
                    for button in upgrade_buttons:
                        if button.handle_event(event):
                            game_state.player.apply_upgrade(button.upgrade)
                            game_state.player.state = PlayerState.ALIVE
                            if hasattr(game_state, 'current_upgrade_buttons'):
                                delattr(game_state, 'current_upgrade_buttons')
                            break
                pygame.display.flip()
                clock.tick(constants.FPS)
                continue

            # ---- GAME LOGIC & DRAWING ----
            # Spawn new waves or enemies if appropriate
            if not game_state.wave_active:
                if (in_game_seconds - game_state.last_wave_time >= game_state.wave_interval or 
                    len(game_state.enemies) == 0):
                    game_state.wave_active = True
                    game_state.wave_enemies_spawned = 0
                    game_state.next_enemy_spawn_time = in_game_seconds + 0.5
            else:
                if in_game_seconds >= game_state.next_enemy_spawn_time and game_state.wave_enemies_spawned < 5:
                    logic.spawn_enemy()
                    game_state.wave_enemies_spawned += 1
                    game_state.next_enemy_spawn_time = in_game_seconds + 0.5
                if game_state.wave_enemies_spawned >= 5:
                    game_state.wave_active = False
                    game_state.last_wave_time = in_game_seconds



            # (Optional) draw any notification (if an upgrade is applied)
            if game_state.notification_message != '' and any("Roll the Dice" in upgrade.name for upgrade in game_state.player.applied_upgrades):
                drawing.draw_notification()

            # Update game objects
            logic.update_enemies()
            logic.update_projectiles()
            logic.spawn_heart()
            logic.update_hearts()

            # Check for game over
            if game_state.player.health <= 0:
                game_state.game_over = True
                if not hasattr(game_state, 'final_time'):
                    game_state.final_time = game_state.in_game_ticks_elapsed // constants.FPS
            drawing.draw_player_state_value_updates()

            if game_state.game_over:
                game_state.fade_alpha = min(game_state.fade_alpha + 10, 255)
                game_state.player.x = game_state.screen_width // 2
                game_state.player.y = game_state.screen_height // 2
                game_state.enemies.clear()  # Remove all enemies
                score.update_high_score()
                show_game_over_screen(game_state.screen, game_state.screen_width, 
                                        game_state.screen_height, game_state.fade_alpha)

            game_state.in_game_ticks_elapsed += 1
            clock.tick(constants.FPS)

            if not game_loop_faded_in:
                if game_state.fade_alpha > 0:
                    fade_from_black_step(game_state.screen, step=20)
                else:
                    game_loop_faded_in = True

            pygame.display.flip()

        # End of the game loop.
        if not game_state.quit:
            continue
        else:
            break

    pygame.mixer.quit()
    pygame.quit()
    exit()

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")  # Create the data directory if it doesn't exist
    main()
