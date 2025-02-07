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
from src.helpers import reset_game, load_music_settings, get_design_mouse_pos, get_text_scaling_factor, fade_from_black, fade_to_black
from src.menu import draw_level_up_menu, draw_pause_menu, draw_upgrades_tab, draw_stats_tab, draw_main_menu
import random

def show_intro_screen(dummy_surface, design_width, design_height):
    # Create text surface using design resolution
    font = pygame.font.Font(None, get_text_scaling_factor(74))
    text = font.render("GOONER INC.", True, constants.WHITE)
    text_rect = text.get_rect(center=(design_width // 2, design_height // 2))
    
    # Fade-in text on the dummy surface
    for alpha in range(0, 256, 5):
        dummy_surface.fill(constants.BLACK)
        text.set_alpha(alpha)
        dummy_surface.blit(text, text_rect)
        
        # Scale and update display
        scaled_surface = pygame.transform.smoothscale(dummy_surface, pygame.display.get_surface().get_size())
        pygame.display.get_surface().blit(scaled_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)
    
    # Display text for 2 seconds (you can still wait on the dummy_surface if needed)
    pygame.time.wait(2000)
    
    # Fade-out to black using an overlay on the dummy surface
    fade_surface = pygame.Surface((design_width, design_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        # Draw the fade overlay onto the dummy_surface
        dummy_surface.blit(fade_surface, (0, 0))
        
        # Scale and update display
        scaled_surface = pygame.transform.smoothscale(dummy_surface, pygame.display.get_surface().get_size())
        pygame.display.get_surface().blit(scaled_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)


def show_game_over_screen(dummy_surface, screen_width, screen_height, alpha):
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
    version_text = version_font.render("Gooner Game v0.1.2", True, constants.WHITE)
    version_text_rect = version_text.get_rect(center=(screen_width // 2, screen_height - 20))  # Position at the bottom
    game_over_surface.blit(version_text, version_text_rect)
    
    # Draw the entire game over surface onto the main screen
    dummy_surface.blit(game_over_surface, (0, 0))

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
    game_state.dummy_surface = pygame.Surface((game_state.DESIGN_WIDTH, game_state.DESIGN_HEIGHT))
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height)
    )
    # Create the player after screen dimensions are known
    game_state.player = Player(
        game_state.DESIGN_WIDTH // 2,
        game_state.DESIGN_HEIGHT // 2,
        game_state.DESIGN_WIDTH,
        game_state.DESIGN_HEIGHT
    )

    # Show the intro screen
    show_intro_screen(game_state.screen, game_state.screen_width, game_state.screen_height)
    
    while True:
        if not pygame.font.get_init() or not pygame.mixer.get_init():
            pygame.font.init()
            pygame.mixer.init()
            
            
        # ---- MAIN MENU LOOP ----
        game_state.in_main_menu = True
        main_menu_faded_in = False
        # game_state.fade_alpha = 255
        
        # Main menu event loop:
        while game_state.in_main_menu:
            game_state.dummy_surface.fill(constants.WHITE)
            start_button, quit_button = draw_main_menu(game_state.dummy_surface)
            
            if not main_menu_faded_in:
                fade_from_black(game_state.dummy_surface, wait_time=5, step=5)
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
                        fade_to_black(game_state.dummy_surface, 5, 5)
                        game_state.dummy_surface.fill(constants.BLACK)
                        break
                    elif quit_button.rect.collidepoint(design_mouse_pos):
                        pygame.quit()
                        exit()  # Immediately exit
            scaled_surface = pygame.transform.smoothscale(game_state.dummy_surface, (game_state.screen_width, game_state.screen_height))
            game_state.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()


        # ---- GAME LOOP ----
        # Start playing music in a separate thread:
        music_thread = threading.Thread(target=load_and_play_music, daemon=True)
        music_thread.start()

        clock = pygame.time.Clock()
        score.reset_score()
        game_state.start_time_ms = pygame.time.get_ticks()

        # Main game loop
        game_state.running = True
        game_loop_faded_in = False
        # Load volume at the start
        constants.music_volume = load_music_settings()

        while game_state.running:
            # Fill background with GREY instead of WHITE
            game_state.dummy_surface.fill(constants.LIGHT_GREY)
                
            # Draw notification
            if game_state.notification_message != '' and any("Roll the Dice" in upgrade.name for upgrade in game_state.player.applied_upgrades):
                drawing.draw_notification()
                    
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
                    # game_state.fade_alpha = 255
                    game_state.player.x = game_state.DESIGN_WIDTH // 2
                    game_state.player.y = game_state.DESIGN_HEIGHT // 2
                    continue
            
            # Convert in_game_ticks to seconds for enemy spawning
            in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS
            
            # Calculate current scaling factor based on in-game ticks
            game_state.enemy_scaling = calculate_enemy_scaling(in_game_seconds)
            game_state.wave_interval = calculate_wave_spawn_interval(in_game_seconds)
            
            # Get current time for cooldowns
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
            font = pygame.font.Font(None, get_text_scaling_factor(36))
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
            time_rect = time_text.get_rect(topright=(game_state.DESIGN_WIDTH - 20, 20))
            # Add a semi-transparent background for better readability
            bg_rect = time_rect.copy()
            bg_rect.inflate_ip(20, 10)  # Make background slightly larger than text
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill(constants.BLACK)
            bg_surface.set_alpha(128)
            game_state.dummy_surface.blit(bg_surface, bg_rect)
            game_state.dummy_surface.blit(time_text, time_rect)
        

            # Draw enemies
            for enemy in game_state.enemies:
                enemy.draw()

            for projectile in game_state.projectiles:
                projectile.draw(game_state.dummy_surface)

            # Draw hearts
            for heart in game_state.hearts:
                pygame.draw.circle(game_state.dummy_surface, constants.PINK, (heart[0], heart[1]), 10)

            # Draw score
            score.draw_score(game_state.dummy_surface)
            game_state.player.draw(game_state.dummy_surface)
            
            # Handle player input (shooting, movement)
            logic.handle_input()
            
            # Update player angle to mouse
            game_state.player.update_angle(pygame.mouse.get_pos())
            
            if not game_loop_faded_in:
                fade_from_black(game_state.dummy_surface, wait_time=5, step=5)
                game_loop_faded_in = True

            # Handle pause menu
            if getattr(game_state, 'paused', False):
                quit_button, resume_button, volume_slider, upgrades_button, stats_button = draw_pause_menu(game_state.dummy_surface)
                
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
                        design_mouse_pos = get_design_mouse_pos(event.pos)
                        if quit_button.rect.collidepoint(design_mouse_pos):
                            # Fade out the game screen to black before returning to main menu:
                            if hasattr(game_state, 'final_time'):
                                delattr(game_state, 'final_time')
                            reset_game()
                            score.reset_score()
                            # game_state.fade_alpha = 255
                            game_state.player.x = game_state.DESIGN_WIDTH // 2
                            game_state.player.y = game_state.DESIGN_HEIGHT // 2
                            
                            game_state.paused = False
                            game_state.in_main_menu = True
                            game_loop_faded_in = False
                            game_state.running = False  # Exit game loop to return to main menu
                            fade_to_black(game_state.dummy_surface, 5, 5)
                            game_state.dummy_surface.fill(constants.BLACK)
                            break
                        elif resume_button.rect.collidepoint(design_mouse_pos):
                            game_state.paused = False
                        elif upgrades_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = True
                            game_state.paused = False
                        elif stats_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_stats = True
                            game_state.paused = False

                scaled_surface = pygame.transform.smoothscale(
                    game_state.dummy_surface, (game_state.screen_width, game_state.screen_height)
                )
                game_state.screen.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                continue
            
            # Handle upgrades tab
            if getattr(game_state, 'showing_upgrades', False):
                close_button = draw_upgrades_tab(game_state.dummy_surface)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_state.running = False

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state.showing_upgrades = False
                        game_state.paused = True  # Return to pause menu

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = get_design_mouse_pos(event.pos)
                        if close_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = False
                            game_state.paused = True  # Return to pause menu

                scaled_surface = pygame.transform.smoothscale(game_state.dummy_surface, (game_state.screen_width, game_state.screen_height))
                game_state.screen.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                continue
            
            # Handle stats tab
            if getattr(game_state, 'showing_stats', False):
                close_button = draw_stats_tab(game_state.dummy_surface)
                # Check for clicks on the close button:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    design_mouse_pos = get_design_mouse_pos(event.pos)
                    if close_button.rect.collidepoint(design_mouse_pos):
                        game_state.showing_stats = False
                        game_state.paused = True  # Return to pause menu
                scaled_surface = pygame.transform.smoothscale(game_state.dummy_surface, (game_state.screen_width, game_state.screen_height))
                game_state.screen.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                continue
            
            if game_state.player.state == PlayerState.LEVELING_UP:
                # Draw the level-up menu and get the persisted buttons
                upgrade_buttons = draw_level_up_menu(game_state.dummy_surface)
                
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

                scaled_surface = pygame.transform.smoothscale(game_state.dummy_surface, (game_state.screen_width, game_state.screen_height))
                game_state.screen.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                clock.tick(constants.FPS)
                continue
            
            
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
                game_state.player.x = game_state.DESIGN_WIDTH // 2
                game_state.player.y = game_state.DESIGN_HEIGHT // 2
                
                # Remove all enemies
                game_state.enemies.clear()  # Clears the list, instantly removing all enemies
                score.update_high_score()
                
                # Display game over screen
                show_game_over_screen(game_state.dummy_surface, game_state.DESIGN_WIDTH, 
                                    game_state.DESIGN_HEIGHT, game_state.fade_alpha)

            # Update display
            game_state.in_game_ticks_elapsed += 1
            clock.tick(constants.FPS)
            # Scale the surface and update game_state.surface
            scaled_surface = pygame.transform.smoothscale(game_state.dummy_surface, (game_state.screen_width, game_state.screen_height))
            game_state.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            
        # End of the game loop.
        # If the game loop ended because the user quit to main menu, we simply
        # continue the outer loop to show the main menu again.
        if not game_state.quit:
            continue
        else:
            # If you ever have a condition to completely exit from the game loop,
            # break out of the outer loop.
            break

    # Finally, when you are ready to completely exit:
    pygame.mixer.quit()
    pygame.quit()
    exit()
    
if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")  # Create the data directory if it doesn't exist
    main()