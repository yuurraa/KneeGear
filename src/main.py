import pygame
from mutagen import File
import threading
import random

import constants
import game_state
import logic
import drawing
import score
from player import Player, PlayerState
from helpers import calculate_angle, reset_game
from menu import draw_level_up_menu, draw_pause_menu

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
    # Double stats every enemy_stat_doubling_time seconds
    scaling_factor = 2 ** (elapsed_seconds / constants.enemy_stat_doubling_time)
    return scaling_factor

def calculate_enemy_spawn_interval(elapsed_seconds):
    # Halve the spawn interval every enemy_spawn_rate_doubling_time_seconds
    spawn_interval = constants.base_enemy_spawn_interval * (2 ** (-elapsed_seconds / constants.enemy_spawn_rate_doubling_time_seconds))
    return max(0.5, spawn_interval)

def load_and_play_music():
    """
    Function to load and play music asynchronously.
    Uses Mutagen to get the duration without loading the entire sound.
    """
    try:
        audio = File(constants.music_path)
        if audio is None or not hasattr(audio.info, 'length'):
            raise ValueError("Unsupported audio format or corrupted file.")
        
        duration = audio.info.length  # Duration in seconds
        print(f"Music duration: {duration} seconds")
        
        pygame.mixer.music.load(constants.music_path)
        pygame.mixer.music.set_volume(constants.music_volume)
        
        # Calculate a random start position, avoiding the last 10 seconds
        max_start = max(0, duration - 10)
        start_pos = random.uniform(0, max_start)
        print(f"Starting music at position: {start_pos} seconds")
        
        pygame.mixer.music.play(-1, start=start_pos)  # -1 for infinite loop
    except Exception as e:
        print(f"Error loading music: {e}")

class State:
    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

class PlayingState(State):
    def handle_event(self, event):
        # Global gameplay events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Push the pause state when ESC is pressed
                state_manager.push(PauseState())
            # If game over, pressing SPACE resets the game
            if event.key == pygame.K_SPACE and game_state.game_over:
                reset_game()
                score.reset_score()

    def update(self):
        # Calculate enemy scaling and spawn interval based on in-game seconds
        in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS
        game_state.enemy_scaling = calculate_enemy_scaling(in_game_seconds)
        game_state.enemy_spawn_interval = calculate_enemy_spawn_interval(in_game_seconds)
        
        # Spawn enemy if sufficient time has passed, or if no enemies exist
        if (in_game_seconds - game_state.last_enemy_spawn_time >= game_state.enemy_spawn_interval):
            logic.spawn_enemy()
            game_state.last_enemy_spawn_time = in_game_seconds
        elif len(game_state.enemies) == 0:
            logic.spawn_enemy()
            game_state.last_enemy_spawn_time = in_game_seconds

        # Handle player input (movement and shooting)
        logic.handle_input()
        # Update player's angle towards the mouse position
        game_state.player.update_angle(pygame.mouse.get_pos())
        
        # Update game entities
        logic.update_enemies()
        logic.update_projectiles()
        logic.spawn_heart()
        logic.update_hearts()

        # Check for game over
        if game_state.player.health <= 0:
            game_state.game_over = True

        # Check if player leveled up and needs to choose an upgrade.
        if game_state.player.state == PlayerState.LEVELING_UP:
            # Ensure we only push LevelUpState if it's not already the current state.
            if not isinstance(state_manager.current_state(), LevelUpState):
                state_manager.push(LevelUpState())

    def draw(self, screen):
        screen.fill(constants.LIGHT_GREY)
        
        # Draw skill icons with cooldown progress
        current_time_s = pygame.time.get_ticks() / 1000.0
        left_cd, right_cd = game_state.player.get_cooldown_progress(current_time_s)
        drawing.draw_skill_icons(left_cd, right_cd)
        
        # Draw experience bar
        drawing.draw_experience_bar()
        
        # Draw stopwatch/time (based on in-game ticks)
        elapsed_seconds = game_state.in_game_ticks_elapsed // constants.FPS
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
        time_rect = time_text.get_rect(topright=(game_state.screen_width - 20, 20))
        bg_rect = time_rect.copy()
        bg_rect.inflate_ip(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill(constants.BLACK)
        bg_surface.set_alpha(128)
        screen.blit(bg_surface, bg_rect)
        screen.blit(time_text, time_rect)
        
        # Draw enemies
        for enemy in game_state.enemies:
            drawing.draw_enemy(enemy)
        
        # Draw projectiles
        for projectile in game_state.projectiles:
            projectile.draw(screen)
        
        # Draw hearts
        for heart in game_state.hearts:
            pygame.draw.circle(screen, constants.PINK, (heart[0], heart[1]), 10)
        
        # Draw score
        score.draw_score(screen)
        
        # Draw player
        game_state.player.draw(screen)
        
        # If game over, handle fade overlay and game over screen
        if game_state.game_over:
            game_state.fade_alpha = min(game_state.fade_alpha + 5, 255)
            drawing.draw_fade_overlay()
            score.update_high_score()
            show_game_over_screen(screen, game_state.screen_width, game_state.screen_height)
        
        # Draw on-screen damage numbers and EXP updates
        drawing.draw_player_state_value_updates()

class PauseState(State):
    def __init__(self):
        # Initialize pause menu UI elements
        self.quit_button, self.volume_slider = draw_pause_menu(game_state.screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Unpause when ESC is pressed again
            state_manager.pop()
        # Handle slider dragging for music volume
        self.volume_slider.handle_event(event)
        # Update button hover state
        self.quit_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If quit button is clicked, exit the game
            if self.quit_button.rect.collidepoint(event.pos):
                game_state.running = False

    def update(self):
        pass

    def draw(self, screen):
        # Draw the underlying game state (the PlayingState)
        playing_state = None
        for s in state_manager.states:
            if isinstance(s, PlayingState):
                playing_state = s
                break
        if playing_state:
            playing_state.draw(screen)
        # Now draw the pause menu overlay on top
        draw_pause_menu(screen)

class LevelUpState(State):
    def __init__(self):
        # Draw the level-up menu and retrieve upgrade buttons
        self.upgrade_buttons = draw_level_up_menu(game_state.screen)

    def handle_event(self, event):
        # Allow pausing even when in the upgrade menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state_manager.push(PauseState())
            return
        if event.type == pygame.QUIT:
            game_state.running = False
        for button in self.upgrade_buttons:
            if button.handle_event(event):
                # Apply the selected upgrade
                button.upgrade.apply(game_state.player)
                game_state.player.state = PlayerState.ALIVE
                if hasattr(game_state, 'current_upgrade_buttons'):
                    delattr(game_state, 'current_upgrade_buttons')
                state_manager.pop()  # Exit the level-up state
                break

    def update(self):
        pass

    def draw(self, screen):
        # Draw the underlying game state (the PlayingState)
        playing_state = None
        for s in state_manager.states:
            if isinstance(s, PlayingState):
                playing_state = s
                break
        if playing_state:
            playing_state.draw(screen)
        # Then draw the level-up menu overlay on top
        draw_level_up_menu(screen)

class StateManager:
    def __init__(self):
        self.states = []

    def push(self, state):
        self.states.append(state)

    def pop(self):
        if self.states:
            self.states.pop()

    def current_state(self):
        if self.states:
            return self.states[-1]
        return None

    def handle_events(self, events):
        current = self.current_state()
        if current:
            for event in events:
                current.handle_event(event)

    def update(self):
        current = self.current_state()
        if current:
            current.update()

    def draw(self, screen):
        current = self.current_state()
        if current:
            current.draw(screen)

# Create a global state manager instance
state_manager = StateManager()

def main():
    pygame.init()
    pygame.mixer.init()
    
    # Set up the display
    info = pygame.display.Info()
    game_state.screen_width = info.current_w
    game_state.screen_height = info.current_h
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height),
        pygame.RESIZABLE
    )
    
    # Create the player (after knowing screen dimensions)
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
    
    # Start the main game loop with the PlayingState
    game_state.running = True
    state_manager.push(PlayingState())
    
    while game_state.running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_state.running = False
        
        state_manager.handle_events(events)
        state_manager.update()
        state_manager.draw(game_state.screen)
        
        pygame.display.flip()
        clock.tick(constants.FPS)
        game_state.in_game_ticks_elapsed += 1
    
    pygame.mixer.quit()
    pygame.quit()

if __name__ == "__main__":
    main()