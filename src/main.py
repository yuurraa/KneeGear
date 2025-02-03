import pygame
from mutagen import File
import threading

import constants
import game_state
import logic
import drawing
import score
from player import Player, PlayerState
from helpers import calculate_angle, reset_game
from menu import draw_level_up_menu, draw_pause_menu
import random

def show_intro_screen(screen, screen_width, screen_height):
    # Create a black background
    screen.fill(constants.BLACK)
    
    # Render the text "GOONER INC."
    font = pygame.font.Font(None, 74)
    text = font.render("GOONER INC.", True, constants.WHITE)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Draw the text on the screen
    screen.blit(text, text_rect)
    pygame.display.flip()
    
    pygame.time.wait(4000)
    
    # Fade out to the gameplay
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(30)

def show_game_over_screen(screen, screen_width, screen_height):
    # Record final time if not already stored
    if not hasattr(game_state, 'final_time'):
        game_state.final_time = game_state.in_game_ticks_elapsed // constants.FPS

    final_time = game_state.final_time
    minutes = final_time // 60
    seconds = final_time % 60

    # Create a black background
    screen.fill(constants.BLACK)
    
    # Use a large font for the "YOU DIED" message
    large_font = pygame.font.Font(None, 74)
    text_large = large_font.render("YOU DIED", True, constants.WHITE)
    text_large_rect = text_large.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
    
    # Use a smaller, uniform font for timer, score, high score, and restart prompt
    small_font = pygame.font.Font(None, 36)
    
    # Render the elapsed time using the final_time
    timer_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
    timer_text_rect = timer_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
    
    # Render the player's score (using score.score from your score module)
    score_text = small_font.render(f"Score: {score.score}", True, constants.WHITE)
    score_text_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
    
    # Render the high score using the same small font
    high_score_text = small_font.render(f"High Score: {score.high_score}", True, constants.WHITE)
    high_score_text_rect = high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
    
    # Render the restart prompt
    restart_text = small_font.render("Press SPACE to restart", True, constants.WHITE)
    restart_text_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    
    # Blit all text elements onto the screen
    screen.blit(text_large, text_large_rect)
    screen.blit(timer_text, timer_text_rect)
    screen.blit(score_text, score_text_rect)
    screen.blit(high_score_text, high_score_text_rect)
    screen.blit(restart_text, restart_text_rect)
    
    pygame.display.flip()

def calculate_enemy_scaling(elapsed_seconds):
    # Double stats every 200 seconds
    # Using 2^(t/200) as scaling formula
    scaling_factor = 2 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor

def calculate_enemy_spawn_interval(elapsed_seconds):
    # Start with base_enemy_spawn_interval and halve it every enemy_spawn_rate_doubling_time_seconds
    spawn_interval = constants.base_enemy_spawn_interval * (2 ** (-elapsed_seconds / constants.enemy_spawn_rate_doubling_time_seconds))
    
    # Set a minimum spawn interval to prevent enemies from spawning too quickly
    return max(0.5, spawn_interval)

def load_and_play_music():
    """
    Function to load and play music asynchronously.
    Uses Mutagen to get the duration without loading the entire sound.
    """
    try:
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

        pygame.mixer.music.play(-1, start= start_pos)  # -1 for infinite loop

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

    # Main game loop
    game_state.running = True
    while game_state.running:
        # Fill background with GREY instead of WHITE
        game_state.screen.fill(constants.LIGHT_GREY)

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
                continue
        
        # Calculate current scaling factor based on in-game ticks
        game_state.enemy_scaling = calculate_enemy_scaling(game_state.in_game_ticks_elapsed / constants.FPS)
        game_state.enemy_spawn_interval = calculate_enemy_spawn_interval(game_state.in_game_ticks_elapsed / constants.FPS)
        
        # Get current time for cooldowns
        current_time_s = pygame.time.get_ticks() / 1000.0
        left_click_cooldown_progress, right_click_cooldown_progress = game_state.player.get_cooldown_progress(current_time_s)
        drawing.draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress)
        drawing.draw_experience_bar()
        
        # Convert in_game_ticks to seconds for enemy spawning
        in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS

        if (in_game_seconds - game_state.last_enemy_spawn_time >= game_state.enemy_spawn_interval):
            logic.spawn_enemy()
            game_state.last_enemy_spawn_time = in_game_seconds
        #if all enemies are dead, spawn an enemy
        elif len(game_state.enemies) == 0:
            logic.spawn_enemy()
            game_state.last_enemy_spawn_time = in_game_seconds

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
            drawing.draw_enemy(enemy)

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
            quit_button, volume_slider = draw_pause_menu(game_state.screen)
            
            for event in pygame.event.get():
                # First handle universal events
                if event.type == pygame.QUIT:
                    game_state.running = False
                
                # Then handle pause-specific events
                volume_slider.handle_event(event)  # Handle ALL events first for smooth dragging
                quit_button.handle_event(event)  # Update button hover state
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state.paused = False  # Unpause
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check quit button after slider to prevent conflict
                    if quit_button.rect.collidepoint(event.pos):
                        game_state.running = False
                    
            # Draw updates and continue loop
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
                        # Apply the selected upgrade
                        button.upgrade.apply(game_state.player)
                        # Reset the state and clear upgrade buttons
                        game_state.player.state = PlayerState.ALIVE
                        if hasattr(game_state, 'current_upgrade_buttons'):
                            delattr(game_state, 'current_upgrade_buttons')
                        break  # Exit the event loop after handling the upgrade

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
        

        # Game Over fade
        if game_state.game_over:
            game_state.fade_alpha = min(game_state.fade_alpha + 5, 255)
            drawing.draw_fade_overlay()
            score.update_high_score()
            show_game_over_screen(game_state.screen, game_state.screen_width, game_state.screen_height)


        # Update display
        game_state.in_game_ticks_elapsed += 1
        pygame.display.flip()
        clock.tick(constants.FPS)

    pygame.mixer.quit()  # Clean up mixer when quitting
    pygame.quit()
if __name__ == "__main__":
    main()