# main.py

import pygame
import constants
import game_state
import logic
import drawing
from helpers import calculate_angle, reset_game


def main():
    pygame.init()
    # Determine full screen dimensions
    game_state.screen_width = pygame.display.Info().current_w
    game_state.screen_height = pygame.display.Info().current_h

    # Set up the fullscreen display
    game_state.screen = pygame.display.set_mode(
        (game_state.screen_width, game_state.screen_height),
        pygame.FULLSCREEN
    )
    clock = pygame.time.Clock()

    # Place the player in the center of the screen
    game_state.player_x = game_state.screen_width // 2
    game_state.player_y = game_state.screen_height // 2

    while game_state.running:
        # Fill background
        game_state.screen.fill(constants.WHITE)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                game_state.running = False

            # Press SPACE to reset if game over
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_state.game_over:
                reset_game()

        # Handle player input (shooting, movement)
        keys = logic.handle_input()
        logic.handle_player_movement(keys)

        # Update player angle to mouse
        mx, my = pygame.mouse.get_pos()
        game_state.player_angle = calculate_angle(game_state.player_x, game_state.player_y, mx, my)

        # Spawn enemies over time
        current_time = pygame.time.get_ticks() / 1000.0
        if not game_state.first_enemy_spawned and current_time >= 1:
            logic.spawn_enemy()
            game_state.first_enemy_spawned = True
            game_state.last_enemy_spawn_time = current_time
        elif game_state.first_enemy_spawned and (current_time - game_state.last_enemy_spawn_time >= constants.enemy_spawn_interval):
            logic.spawn_enemy()
            game_state.last_enemy_spawn_time = current_time

        # Update all logic
        logic.update_enemies()
        logic.update_projectiles()
        logic.update_enemy_bullets()
        logic.update_enemy_aoe_bullets()
        logic.update_tank_pellets()
        logic.spawn_heart()
        logic.update_hearts()

        # Draw projectiles first so enemies/players appear atop them
        drawing.draw_projectiles()

        # Draw player
        drawing.draw_player(game_state.player_x, game_state.player_y, game_state.player_angle)

        # Draw enemies
        for enemy in game_state.enemies:
            drawing.draw_enemy(enemy["x"], enemy["y"], enemy["health"], enemy["type"])

        # Draw enemy bullets
        for bullet in game_state.enemy_bullets:
            pygame.draw.circle(game_state.screen, constants.RED, (int(bullet[0]), int(bullet[1])), 5)

        # Draw enemy AOE bullets
        for bullet in game_state.enemy_aoe_bullets:
            pygame.draw.circle(game_state.screen, constants.PURPLE, (int(bullet[0]), int(bullet[1])), 5)

        # Draw hearts
        for heart in game_state.hearts:
            pygame.draw.circle(game_state.screen, constants.PINK, (heart[0], heart[1]), 10)

        # Draw tank pellets
        for pellet in game_state.tank_pellets:
            pygame.draw.circle(game_state.screen, (139, 69, 19), (int(pellet[0]), int(pellet[1])), 3)

        # Draw player's health bar
        drawing.draw_health_bar(20, 20, game_state.player_health, 100, constants.TRANSLUCENT_GREEN)

        # Game Over fade
        if game_state.game_over:
            game_state.fade_alpha = min(game_state.fade_alpha + 5, 255)
            drawing.draw_fade_overlay()

        # Check if player's health is depleted
        if game_state.player_health <= 0:
            game_state.game_over = True

        # Update display
        pygame.display.flip()
        clock.tick(constants.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
