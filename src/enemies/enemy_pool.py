import random
import src.engine.game_state as game_state
import src.engine.constants as constants
from src.enemies.basic import BasicEnemy
from src.enemies.tank import TankEnemy
from src.enemies.charger import ChargerEnemy
from src.enemies.sniper import SniperEnemy

class EnemyPool:
    def __init__(self):
        # Define enemy types along with their spawn weights.
        self.enemy_types = [
            (BasicEnemy, 0.6),
            (TankEnemy, 0.3),
            (ChargerEnemy, 0.2),
            (SniperEnemy, 0.2)
        ]
    
    def spawn_enemy(self):
        # Determine spawn position based on a random side.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(0, game_state.screen_width)
            y = -20
        elif side == "bottom":
            x = random.randint(0, game_state.screen_width)
            y = game_state.screen_height + 20
        elif side == "left":
            x = -20
            y = random.randint(0, game_state.screen_height)
        else:  # "right"
            x = game_state.screen_width + 20
            y = random.randint(0, game_state.screen_height)
        
        # Use weighted random selection for enemy type.
        EnemyClass = random.choices(
            population=[enemy_type for enemy_type, _ in self.enemy_types],
            weights=[weight for _, weight in self.enemy_types],
            k=1
        )[0]
        
        # Create a new enemy instance.
        enemy = EnemyClass(x, y, game_state.enemy_scaling)
        game_state.enemies.append(enemy)
    
    def update(self):
        # Update each enemy and remove those that have finished dying.
        for enemy in game_state.enemies[:]:
            enemy.update(game_state.player.x, game_state.player.y, game_state)
            # Check if the enemy is dying and its death animation is complete.
            if enemy.dying and (enemy.current_tick - enemy.death_animation_start_tick) > enemy.death_animation_duration * constants.FPS:
                game_state.enemies.remove(enemy)
    
    def draw(self, screen):
        # Draw each enemy.
        for enemy in game_state.enemies:
            enemy.draw()
