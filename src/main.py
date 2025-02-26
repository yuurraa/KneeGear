import pygame
import threading
import os  # Import os module to check for file existence

import src.engine.constants as constants
import src.engine.game_state as game_state
import src.engine.logic as logic
import src.ui.drawing as drawing
import src.engine.score as score
from src.player.player import Player, PlayerState
from src.engine.helpers import (
    reset_game, fade_to_black, fade_from_black_step, load_skin_selection, save_skin_selection
)
from src.ui.menu import (
    draw_level_up_menu, draw_pause_menu, draw_upgrades_tab, draw_stats_tab, 
    draw_main_menu, draw_skin_selection_menu
)
from src.engine.music_handler import (
    MUSIC_END_EVENT, switch_playlist, previous_song, next_song, 
    load_and_play_music
)
from src.enemies.enemy_pool import EnemyPool


def main():
    pygame.init()
    pygame.mixer.init()
    
    # Initialize display and game state.
    game_state.screen_width = pygame.display.Info().current_w
    game_state.screen_height = pygame.display.Info().current_h

    # Set a reference design resolution (adjust these values as needed)
    if not hasattr(game_state, 'design_width'):
        game_state.design_width = 1920
    if not hasattr(game_state, 'design_height'):
        game_state.design_height = 1080

    # Then create your display as usual
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height), pygame.SCALED, pygame.FULLSCREEN
    )
    game_state.player = Player(
        game_state.screen_width // 2,
        game_state.screen_height // 2,
        game_state.screen_width,
        game_state.screen_height
    )
    
    drawing.show_intro_screen(game_state.screen, game_state.screen_width, game_state.screen_height)

    if not pygame.mixer.music.get_busy():
        music_thread = threading.Thread(target=load_and_play_music, daemon=True)
        music_thread.start()

    load_skin_selection()

    # Initialize state flags.
    game_state.in_main_menu = True
    game_state.skin_menu = False
    game_state.running = False
    game_state.paused = False
    game_state.game_over = False
    main_menu_faded_in = False
    game_loop_faded_in = False
    game_state.skin_buttons, game_state.close_button = draw_skin_selection_menu(game_state.screen)

    # Create a clock once for the game loop.
    clock = pygame.time.Clock()
    enemy_pool = EnemyPool()  # Ideally created once (adjust as needed)

    # Main loop (state-machine style).
    while True:
        # Poll events once per frame.
        events = pygame.event.get()
        for event in events:
            if event.type == MUSIC_END_EVENT:
                next_song()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # ---------------- Main Menu State ----------------
        if game_state.in_main_menu:
            game_state.screen.fill(constants.WHITE)
            start_button, quit_button, skin_button = draw_main_menu(game_state.screen)
            if not main_menu_faded_in:
                if game_state.fade_alpha > 0:
                    fade_from_black_step(game_state.screen, step=30)
                else:
                    main_menu_faded_in = True

            for event in events:
                start_button.handle_event(event)
                skin_button.handle_event(event)
                quit_button.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    design_mouse_pos = pygame.mouse.get_pos()
                    if start_button.rect.collidepoint(design_mouse_pos):
                        main_menu_faded_in = False
                        game_state.in_main_menu = False
                        game_state.running = True
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        game_state.fade_alpha = 255
                    elif skin_button.rect.collidepoint(design_mouse_pos):
                        game_state.skin_menu = True
                        game_state.in_main_menu = False
                        game_state.running = False
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        game_state.fade_alpha = 255
                    elif quit_button.rect.collidepoint(design_mouse_pos):
                        pygame.quit()
                        exit()
            pygame.display.flip()
            continue  # Process next frame
        
        # ---------------- Skin Selection State ----------------
        if game_state.skin_menu:
            clock.tick(constants.FPS)  # Regulate frame rate
            # Redraw entire skin selection menu
            game_state.screen.fill(constants.WHITE)
            draw_skin_selection_menu(game_state.screen)
            # Draw overlay, title, and buttons each frame
            for btn in game_state.skin_buttons:
                btn.draw(game_state.screen)
                    
            if game_state.fade_alpha > 0:
                fade_from_black_step(game_state.screen, step=30)

            for event in events:
                for btn in game_state.skin_buttons:
                    btn.handle_event(event)
                game_state.close_button.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    design_mouse_pos = pygame.mouse.get_pos()
                    if game_state.close_button.rect.collidepoint(design_mouse_pos):
                        game_state.skin_menu = False
                        game_state.in_main_menu = True
                        game_state.running = False  
                        fade_to_black(game_state.screen, 5, 10)
                        game_state.screen.fill(constants.BLACK)
                        game_state.fade_alpha = 255  # Reset fade alpha for main menu
                        main_menu_faded_in = False  # Reset local fade flag for main menu
                    else:
                        for btn in game_state.skin_buttons:
                            if btn.rect.collidepoint(design_mouse_pos):
                                btn.trigger_glow()
                                game_state.player.change_skin(btn.skin_id)
                                save_skin_selection()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state.skin_menu = False
                    game_state.in_main_menu = True
                    game_state.running = False
                    fade_to_black(game_state.screen, 5, 10)
                    game_state.screen.fill(constants.BLACK)
                    game_state.fade_alpha = 255  # Reset fade alpha for main menu
                    main_menu_faded_in = False  # Reset local fade flag for main menu
            pygame.display.flip()
            continue

        # ---------------- Game Loop State ----------------
        if game_state.running:
            clock.tick(constants.FPS)
            game_state.screen.fill(constants.LIGHT_GREY)
            
            # Filter events for in-game processing.
            filtered_events = []
            escHandled = False
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not game_state.game_over and not escHandled:
                        if not game_state.paused:
                            game_state.pause_background = game_state.screen.copy()
                        game_state.paused = not game_state.paused
                        game_state.showing_stats = False
                        game_state.showing_upgrades = False
                        escHandled = True
                else:
                    filtered_events.append(event)
            events = filtered_events

            reset_triggered = False
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state.game_over:
                    reset_game()
                    game_state.screen.fill(constants.LIGHT_GREY)
                    game_loop_faded_in = False
                    game_state.fade_alpha = 255
                    reset_triggered = True
                    break
            if reset_triggered:
                continue

            if (not getattr(game_state, 'paused', False) and 
                game_state.player.state != PlayerState.LEVELING_UP and 
                not getattr(game_state, 'showing_upgrades', False) and 
                not getattr(game_state, 'showing_stats', False)):
                logic.handle_input()
                game_state.player.update_angle(pygame.mouse.get_pos())

            enemy_pool.draw(game_state.screen)
            game_state.bullet_pool.draw(game_state.screen)
            for heart in game_state.hearts:
                heart.update()
                heart.draw(game_state.screen)
            game_state.player.draw(game_state.screen)
            score.draw_score(game_state.screen)
            
            in_game_seconds = game_state.in_game_ticks_elapsed / constants.FPS
            game_state.enemy_scaling = logic.calculate_enemy_scaling(in_game_seconds)
            game_state.wave_interval = logic.calculate_wave_spawn_interval(in_game_seconds)
            left_click_cooldown_progress, right_click_cooldown_progress = game_state.player.get_cooldown_progress()
            fps = clock.get_fps()
            drawing.draw_skill_icons(left_click_cooldown_progress, right_click_cooldown_progress, fps)
            drawing.draw_experience_bar()
            
            elapsed_seconds = game_state.in_game_ticks_elapsed // constants.FPS
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            time_text = game_state.FONTS["medium"].render(f"Time: {minutes:02d}:{seconds:02d}", True, constants.WHITE)
            time_rect = time_text.get_rect(topright=(game_state.screen_width - 20, 20))
            bg_rect = time_rect.copy()
            bg_rect.inflate_ip(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill(constants.BLACK)
            bg_surface.set_alpha(128)
            game_state.screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(game_state.screen, (0, 0, 0), bg_rect, 2)
            game_state.screen.blit(time_text, time_rect)
            
            drawing.draw_notification()
            drawing.draw_player_state_value_updates()
            
            if getattr(game_state, 'paused', False):
                quit_button, resume_button, volume_slider, upgrades_button, stats_button, playlist_button, previous_button, skip_button = draw_pause_menu(game_state.screen)
                for event in events:
                    volume_slider.handle_event(event)
                    quit_button.handle_event(event)
                    resume_button.handle_event(event)
                    upgrades_button.handle_event(event)
                    stats_button.handle_event(event)
                    playlist_button.handle_event(event)
                    previous_button.handle_event(event)
                    skip_button.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = pygame.mouse.get_pos()
                        if quit_button.rect.collidepoint(design_mouse_pos):
                            reset_game()
                            game_state.in_main_menu = True
                            game_loop_faded_in = False
                            fade_to_black(game_state.screen, 5, 10)
                            game_state.screen.fill(constants.BLACK)
                            game_state.running = False
                            game_state.fade_alpha = 255  # Reset fade alpha for main menu
                            main_menu_faded_in = False  # Reset local fade flag for main menu
                            break
                        elif resume_button.rect.collidepoint(design_mouse_pos):
                            game_state.paused = False
                        elif upgrades_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = True
                            game_state.paused = False
                        elif stats_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_stats = True
                            game_state.paused = False
                        elif playlist_button.rect.collidepoint(design_mouse_pos):
                            switch_playlist()
                        elif previous_button.rect.collidepoint(design_mouse_pos):
                            previous_song()
                        elif skip_button.rect.collidepoint(design_mouse_pos):
                            next_song()
                pygame.display.flip()
                continue
            
            if getattr(game_state, 'showing_upgrades', False):
                close_button = draw_upgrades_tab(game_state.screen)
                for event in events:
                    close_button.handle_event(event)
                    if event.type == pygame.QUIT:
                        game_state.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state.showing_upgrades = False
                        game_state.paused = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = pygame.mouse.get_pos()
                        if close_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_upgrades = False
                            game_state.paused = True
                pygame.display.flip()
                continue
            
            if getattr(game_state, 'showing_stats', False):
                close_button = draw_stats_tab(game_state.screen)
                for event in events:
                    close_button.handle_event(event)
                    if event.type == pygame.QUIT:
                        game_state.running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        game_state.showing_stats = False
                        game_state.paused = True
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        design_mouse_pos = pygame.mouse.get_pos()
                        if close_button.rect.collidepoint(design_mouse_pos):
                            game_state.showing_stats = False
                            game_state.paused = True
                pygame.display.flip()
                continue
            
            if game_state.player.state == PlayerState.LEVELING_UP:
                # Record the time when the level up menu is first shown
                if not hasattr(game_state, 'level_up_start_time'):
                    game_state.level_up_start_time = pygame.time.get_ticks()

                upgrade_buttons = draw_level_up_menu(game_state.screen)

                # Calculate elapsed time since the menu was shown
                elapsed = pygame.time.get_ticks() - game_state.level_up_start_time

                # If less than 500ms have passed, skip processing clicks
                if elapsed < 500:
                    pygame.display.flip()
                    continue

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
                            # Remove the timer attribute so that it resets next time
                            if hasattr(game_state, 'level_up_start_time'):
                                delattr(game_state, 'level_up_start_time')
                            break

                pygame.display.flip()
                continue

            
            # Wave spawning logic
            if not game_state.wave_active:
                if (in_game_seconds - game_state.last_wave_time >= game_state.wave_interval or 
                    len(game_state.enemies) == 0):
                    game_state.wave_active = True
                    game_state.wave_enemies_spawned = 0
                    game_state.next_enemy_spawn_time = in_game_seconds + 0.5
            else:
                if in_game_seconds >= game_state.next_enemy_spawn_time and game_state.wave_enemies_spawned < 5:
                    enemy_pool.spawn_enemy()
                    game_state.wave_enemies_spawned += 1
                    game_state.next_enemy_spawn_time = in_game_seconds + 0.5
                if game_state.wave_enemies_spawned >= 5:
                    game_state.wave_active = False
                    game_state.last_wave_time = in_game_seconds

            enemy_pool.update()
            logic.update_projectiles()
            logic.spawn_heart()
            logic.update_hearts()

            if game_state.player.health <= 0:
                if not game_state.game_over:  # Only do this once
                    game_state.game_over = True
                    game_state.final_time = game_state.in_game_ticks_elapsed // constants.FPS
                    game_state.final_score = score.score

            if game_state.game_over:
                game_state.fade_alpha = min(game_state.fade_alpha + 10, 255)
                game_state.player.x = game_state.screen_width // 2
                game_state.player.y = game_state.screen_height // 2
                game_state.enemies.clear()
                score.update_high_score()
                drawing.show_game_over_screen(game_state.screen, game_state.screen_width, game_state.screen_height, game_state.fade_alpha)

            game_state.in_game_ticks_elapsed += 1
            if not game_loop_faded_in:
                if game_state.fade_alpha > 0:
                    fade_from_black_step(game_state.screen, step=20)
                else:
                    game_loop_faded_in = True

            pygame.display.flip()
            continue
        
        pygame.display.update()
        # End of the game loop.
        if not game_state.quit:
            continue
        else:
            break

    # (Optional: if you have any other state, process it here.)
    pygame.mixer.quit()
    pygame.quit()
    exit()

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")  # Create the data directory if it doesn't exist
    main()
