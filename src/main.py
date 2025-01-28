import pygame
import constants
import game_state
import logic
import drawing
import score
from player import Player, PlayerState
from helpers import calculate_angle, reset_game
from menu import draw_level_up_menu
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
    
    # Wait for 2 seconds (2000 milliseconds)
    pygame.time.wait(2000)
    
    # Fade out to the gameplay
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill(constants.BLACK)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(30)

def show_game_over_screen(screen, screen_width, screen_height):
    # Create a black background
    screen.fill(constants.BLACK)
    
    # Render the text "YOU DIED"
    font_large = pygame.font.Font(None, 74)
    text_large = font_large.render("YOU DIED", True, constants.WHITE)
    text_large_rect = text_large.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    
    # Render the text "Press SPACE to restart"
    font_small = pygame.font.Font(None, 36)
    text_small = font_small.render("Press SPACE to restart", True, constants.WHITE)
    text_small_rect = text_small.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
    
    # Draw the text on the screen
    screen.blit(text_large, text_large_rect)
    screen.blit(text_small, text_small_rect)
    pygame.display.flip()

def calculate_enemy_scaling(elapsed_seconds):
    # Double stats every 200 seconds
    # Using 2^(t/200) as scaling formula
    scaling_factor = 2 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer
    
    # Load and start background music
    try:
        music = pygame.mixer.music.load(constants.music_path)
        duration = pygame.mixer.Sound(constants.music_path).get_length()  # Get song duration
        pygame.mixer.music.set_volume(constants.music_volume)
        start_pos = random.uniform(0, duration - 10)  # Random start position (avoiding last 10 seconds)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        pygame.mixer.music.set_pos(start_pos)  # Set random start position
    except Exception as e:
        print(f"Error loading music: {e}")
    
    # After setting up the display
    game_state.screen_width = pygame.display.Info().current_w
    game_state.screen_height = pygame.display.Info().current_h

    # Set up the fullscreen display
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height),
        # pygame.FULLSCREEN
        pygame.RESIZABLE
    )

    # Create the player after screen dimensions are known
    game_state.player = Player(
        game_state.screen_width // 2,
        game_state.screen_height // 2,
        game_state.screen_width,
        game_state.screen_height
    )

    clock = pygame.time.Clock()

    # Show the intro screen
    show_intro_screen(game_state.screen, game_state.screen_width, game_state.screen_height)

    # Initialize score and start time
    score.reset_score()
    game_state.start_time_ms = pygame.time.get_ticks()

    while game_state.running:
        # Fill background with GREY instead of WHITE
        game_state.screen.fill(constants.LIGHT_GREY)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                game_state.running = False

            # Press SPACE to reset if game over
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state.game_over:
                reset_game()
                score.reset_score()
                continue


        # Calculate current scaling factor based on elapsed time
        current_time_ms = pygame.time.get_ticks()
        elapsed_seconds = (current_time_ms - game_state.start_time_ms) // 1000
        game_state.enemy_scaling = calculate_enemy_scaling(elapsed_seconds)
        # Spawn enemies over time
        current_time_s = current_time_ms / 1000.0
        left_click_cooldown_progress, right_click_cooldown_progress = game_state.player.get_cooldown_progress(current_time_s)
        drawing.draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress)
        drawing.draw_experience_bar()
        
        if not game_state.first_enemy_spawned and current_time_s >= 1:
            logic.spawn_enemy()  # Pass scaling factor to spawn_enemy
            game_state.first_enemy_spawned = True
            game_state.last_enemy_spawn_time = current_time_s
        elif game_state.first_enemy_spawned and (current_time_s - game_state.last_enemy_spawn_time >= constants.enemy_spawn_interval):
            logic.spawn_enemy()  # Pass scaling factor to spawn_enemy
            game_state.last_enemy_spawn_time = current_time_s

        # Draw stopwatch
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - game_state.start_time_ms) // 1000
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

        
        # Handle level up menu
        if game_state.player.state == PlayerState.LEVELING_UP:
            upgrade_buttons = draw_level_up_menu(game_state.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    game_state.running = False
                
                for button in upgrade_buttons:
                    if button.handle_event(event):
                        # Apply the selected upgrade
                        button.upgrade.apply(game_state.player)
                        # Reset the state and clear upgrade options
                        game_state.player.state = PlayerState.ALIVE
                        if hasattr(game_state, 'current_upgrade_options'):
                            delattr(game_state, 'current_upgrade_options')
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
            game_state.game_over = True      # Draw damage numbers
        drawing.draw_player_state_value_updates()
        

        # Game Over fade
        if game_state.game_over:
            game_state.fade_alpha = min(game_state.fade_alpha + 5, 255)
            drawing.draw_fade_overlay()
            score.update_high_score()
            show_game_over_screen(game_state.screen, game_state.screen_width, game_state.screen_height)



        # Update display
        pygame.display.flip()
        clock.tick(constants.FPS)

    pygame.mixer.quit()  # Clean up mixer when quitting
    pygame.quit()
if __name__ == "__main__":
    main()