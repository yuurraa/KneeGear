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
from src.helpers import calculate_angle, reset_game, load_music_settings, save_music_settings
from src.menu import draw_level_up_menu, draw_pause_menu, draw_upgrades_tab
import random

def show_intro_screen(screen, screen_width, screen_height):
    # Create text surface
    font = pygame.font.Font(None, 74)
    text = font.render("GOONER INC.", True, constants.WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Fade-in text
    for alpha in range(0, 256, 5):
        screen.fill(constants.BLACK)
        text.set_alpha(alpha)
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(10)
    
    # Display text for 2 seconds
    pygame.time.wait(2000)
    
    # Fade-out to black
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)

def show_game_over_screen(screen, screen_width, screen_height, alpha):
    # Create a surface with per-pixel alpha for fading
    game_over_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    # Fill with black background using the provided alpha for transparency
    game_over_surface.fill((0, 0, 0, alpha))
    
    # Render "YOU DIED" text
    large_font = pygame.font.Font(None, 74)
    text_large = large_font.render("YOU DIED", True, constants.WHITE)
    text_large_rect = text_large.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
    game_over_surface.blit(text_large, text_large_rect)
    
    # Render time, score, high score, and restart prompt
    small_font = pygame.font.Font(None, 36)
    
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
    version_font = pygame.font.Font(None, 24)  # Smaller font size
    version_text = version_font.render("Gooner Game v0.1.1", True, constants.WHITE)
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

    # Set up the resizable display
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height),
        pygame.RESIZABLE
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

    # Start loading and playing music in a separate thread
    music_thread = threading.Thread(target=load_and_play_music, daemon=True)
    music_thread.start()

    clock = pygame.time.Clock()

    # Initialize score and start time
    score.reset_score()
    game_state.start_time_ms = pygame.time.get_ticks()
    game_state.fade_alpha = 255 

    # Main game loop
    game_state.running = True
    scroll_offset = 0

    # Load volume at the start
    constants.music_volume = load_music_settings()

    while game_state.running:
        # Fill background with GREY instead of WHITE
        game_state.screen.fill(constants.LIGHT_GREY)
        
        # Draw fade overlay if active
        if game_state.fade_alpha > 0:
            fade_overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
            fade_overlay.fill(constants.BLACK)
            fade_overlay.set_alpha(game_state.fade_alpha)
            game_state.screen.blit(fade_overlay, (0, 0))

        # Fade-in (when no active fade-out)
        if not game_state.game_over and not game_state.restart_fade_out:
            if game_state.fade_alpha > 0:
                game_state.fade_alpha = max(game_state.fade_alpha - 10, 0)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not game_state.game_over:
                    game_state.paused = True

            # Press SPACE to reset if game over
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state.game_over:
                # Reset final_time as part of your reset routine
                if hasattr(game_state, 'final_time'):
                    delattr(game_state, 'final_time')
                reset_game()
                score.reset_score()
                game_state.fade_alpha = 255
                game_state.player.x = game_state.screen_width // 2
                game_state.player.y = game_state.screen_height // 2
                continue
        
        # Convert in_game_ticks to seconds for enemy spawning
        in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS
        
        # Calculate current scaling factor based on in-game ticks
        game_state.enemy_scaling = calculate_enemy_scaling(in_game_seconds)
        game_state.wave_interval = calculate_wave_spawn_interval(in_game_seconds)
        
        # Get current time for cooldowns
        current_time_s = pygame.time.get_ticks() / 1000.0
        left_click_cooldown_progress, right_click_cooldown_progress = game_state.player.get_cooldown_progress()
        drawing.draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress)
        drawing.draw_experience_bar()
        

        if not game_state.wave_active:
            # Start a new wave if enough time has passed OR if there are no enemies
            if (in_game_seconds - game_state.last_wave_time >= game_state.wave_interval or 
                len(game_state.enemies) == 0):
                # Start a new wave
                game_state.wave_active = True
                game_state.wave_enemies_spawned = 0
                game_state.next_enemy_spawn_time = in_game_seconds + 0.5
        else:
            # If a wave is active, spawn enemies at 0.5 second intervals until 5 enemies have been spawned.
            if in_game_seconds >= game_state.next_enemy_spawn_time and game_state.wave_enemies_spawned < 5:
                logic.spawn_enemy()
                game_state.wave_enemies_spawned += 1
                game_state.next_enemy_spawn_time = in_game_seconds + 0.5

            # Once 5 enemies have been spawned, finish the wave and reset the wave timer.
            if game_state.wave_enemies_spawned >= 5:
                game_state.wave_active = False
                game_state.last_wave_time = in_game_seconds
            
            

        # Draw stopwatch using in_game_ticks
        elapsed_seconds = game_state.in_game_ticks_elapsed // constants.FPS
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
        time_rect = time_text.get_rect(topright=(game_state.screen_width - 20, 20))
        # Add a semi-transparent background for better readability
        bg_rect = time_rect.copy()
        bg_rect.inflate_ip(20, 10)  # Make background slightly larger than text
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill(constants.BLACK)
        bg_surface.set_alpha(128)
        game_state.screen.blit(bg_surface, bg_rect)
        game_state.screen.blit(time_text, time_rect)
        
        # Draw enemies
        for enemy in game_state.enemies:
            enemy.draw()

        for projectile in game_state.projectiles:
            projectile.draw(game_state.screen)

        # Draw hearts
        for heart in game_state.hearts:
            pygame.draw.circle(game_state.screen, constants.PINK, (heart[0], heart[1]), 10)

        # Draw score
        score.draw_score(game_state.screen)
        game_state.player.draw(game_state.screen)

        # Handle pause menu
        if getattr(game_state, 'paused', False):
            quit_button, resume_button, volume_slider, upgrades_button = draw_pause_menu(game_state.screen)
            
            for event in pygame.event.get():
                # First handle universal events
                if event.type == pygame.QUIT:
                    game_state.running = False
                
                # Then handle pause-specific events
                volume_slider.handle_event(event)
                quit_button.handle_event(event)
                resume_button.handle_event(event)
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state.paused = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if quit_button.rect.collidepoint(event.pos):
                        game_state.running = False
                    elif resume_button.rect.collidepoint(event.pos):
                        game_state.paused = False
                    elif upgrades_button.rect.collidepoint(event.pos):
                        game_state.showing_upgrades = True
                        game_state.paused = False  # Close pause menu when opening upgrades tab
            
            # Draw updates and continue loop
            pygame.display.flip()
            continue
        
        # Handle upgrades tab
        if getattr(game_state, 'showing_upgrades', False):
            close_button = draw_upgrades_tab(game_state.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state.showing_upgrades = False
                    game_state.paused = True  # Return to pause menu

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if close_button.rect.collidepoint(event.pos):
                        game_state.showing_upgrades = False
                        game_state.paused = True  # Return to pause menu

                # Handle scrolling
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        game_state.scroll_offset = max(game_state.scroll_offset - 20, 0)
                    elif event.button == 5:  # Scroll down
                        game_state.scroll_offset += 20

            pygame.display.flip()
            continue
        
        if game_state.player.state == PlayerState.LEVELING_UP:
            # Draw the level-up menu and get the persisted buttons
            upgrade_buttons = draw_level_up_menu(game_state.screen)
            
            # Process events only for the level-up menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.running = False
                    break  # Exit the event loop if quitting
                
                # Add this block to handle ESC key during level-up menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Cancel the level-up menu and bring up the pause menu immediately
                    game_state.paused = True
                    break  # Break out of the level-up menu event loop

                # Handle button events for upgrades
                for button in upgrade_buttons:
                    if button.handle_event(event):
                        # Apply the selected upgrade using apply_upgrade method
                        game_state.player.apply_upgrade(button.upgrade)  # Use apply_upgrade method
                        # Reset the state and clear upgrade buttons
                        game_state.player.state = PlayerState.ALIVE
                        if hasattr(game_state, 'current_upgrade_buttons'):
                            delattr(game_state, 'current_upgrade_buttons')
                        break

            pygame.display.flip()
            clock.tick(constants.FPS)
            continue
        
        # Handle player input (shooting, movement)
        logic.handle_input()
        
        # Update player angle to mouse
        game_state.player.update_angle(pygame.mouse.get_pos())
        
        # Update all logic
        logic.update_enemies()
        logic.update_projectiles()
        logic.spawn_heart()
        logic.update_hearts()

        # Check if player's health is depleted
        if game_state.player.health <= 0:
            game_state.game_over = True
            if not hasattr(game_state, 'final_time'):
                game_state.final_time = game_state.in_game_ticks_elapsed // constants.FPS
        drawing.draw_player_state_value_updates()
        
        if game_state.game_over:
            # Increase fade effect for game over screen
            game_state.fade_alpha = min(game_state.fade_alpha + 10, 255)
            
            # Prevent player from moving
            game_state.player.x = game_state.screen_width // 2
            game_state.player.y = game_state.screen_height // 2
            
            # Remove all enemies
            game_state.enemies.clear()  # Clears the list, instantly removing all enemies
            score.update_high_score()
            
            # Display game over screen
            show_game_over_screen(game_state.screen, game_state.screen_width, 
                                game_state.screen_height, game_state.fade_alpha)

        # Update display
        game_state.in_game_ticks_elapsed += 1
        pygame.display.flip()
        clock.tick(constants.FPS)

        # Draw notification
        drawing.draw_notification()

    pygame.mixer.quit()  # Clean up mixer when quitting
    pygame.quit()
if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")  # Create the data directory if it doesn't exist
    main()