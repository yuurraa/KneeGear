import random
import src.engine.game_state as game_state
import src.engine.constants as constants
from src.enemies.basic import BasicEnemy
from src.enemies.tank import TankEnemy
from src.enemies.charger import ChargerEnemy
from src.enemies.sniper import SniperEnemy
from src.engine.helpers import get_ui_scaling_factor

ui_scaling_factor = get_ui_scaling_factor()

class EnemyPool:
    def __init__(self, max_enemies=50):
        # Define enemy types along with their spawn weights.
        self.enemy_types = [
            (BasicEnemy, 0.6),
            (TankEnemy, 0.3),
            (ChargerEnemy, 0.2),
            (SniperEnemy, 0.2)
        ]
        self.pool = []
        for _ in range(max_enemies):
            enemy_class = random.choices(
                population=[enemy_type for enemy_type, _ in self.enemy_types],
                weights=[weight for _, weight in self.enemy_types],
                k=1
            )[0]
            self.pool.append(enemy_class(0, 0, 1))  # Default off-screen, inactive
    
    def spawn_enemy(self):
        # Determine spawn position based on a random side.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(0, game_state.screen_width)
            y = -40 * ui_scaling_factor
        elif side == "bottom":
            x = random.randint(0, game_state.screen_width)
            y = game_state.screen_height + 40 * ui_scaling_factor
        elif side == "left":
            x = -40 * ui_scaling_factor
            y = random.randint(0, game_state.screen_height)
        else:  # "right"
            x = game_state.screen_width + 40 * ui_scaling_factor
            y = random.randint(0, game_state.screen_height)
        
        # First, filter the pool for inactive enemies.
        inactive_enemies = [enemy for enemy in self.pool if not getattr(enemy, 'active', False)]
        if inactive_enemies:
            # Determine weights for each inactive enemy based on its type.
            weights = []
            for enemy in inactive_enemies:
                # Find the weight for this enemy's type from self.enemy_types.
                for enemy_class, weight in self.enemy_types:
                    if isinstance(enemy, enemy_class):
                        weights.append(weight)
                        break
                else:
                    weights.append(1)  # Default weight if not found.
            chosen_enemy = random.choices(inactive_enemies, weights=weights, k=1)[0]
            chosen_enemy.reset(x, y, game_state.enemy_scaling)
            chosen_enemy.active = True  # Mark it as in use.
            game_state.enemies.append(chosen_enemy)
            return

        # If no inactive enemy is available, create a new one using weighted selection.
        EnemyClass = random.choices(
            population=[enemy_type for enemy_type, _ in self.enemy_types],
            weights=[weight for _, weight in self.enemy_types],
            k=1
        )[0]
        
        enemy = EnemyClass(x, y, game_state.enemy_scaling)
        enemy.active = True  # Mark new enemy as active.
        game_state.enemies.append(enemy)
        self.pool.append(enemy)  # Add new enemy to the pool for reuse.
    
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
