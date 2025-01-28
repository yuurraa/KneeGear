from dataclasses import dataclass
from typing import Callable, List
import random
from math import ceil, floor
from player import Player

@dataclass
class Upgrade:
    name: str
    description: str
    apply: Callable[[Player], None]
    icon: str  # Could be used for future UI improvements

class UpgradePool:
    def __init__(self):
        self.upgrades = [
            Upgrade(
                name="Rapid Fire",
                description="Decrease basic attack cooldown by 30%",
                apply=lambda player: setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Heavy Bullets",
                description="Increase basic attack damage by 40%",
                apply=lambda player: setattr(player, 'basic_bullet_damage_multiplier', 
                                           player.basic_bullet_damage_multiplier * 1.4),
                icon="💥"
            ),
            Upgrade(
                name="Swift Shot",
                description="Increase basic bullet speed by 40%",
                apply=lambda player: setattr(player, 'basic_bullet_speed_multiplier', 
                                           player.basic_bullet_speed_multiplier * 1.4),
                icon="🚀"
            ),
            Upgrade(
                name="Special Force",
                description="Increase special attack damage by 40%",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 1.4),
                icon="⭐"
            ),
            Upgrade(
                name="Quick Charge",
                description="Decrease special attack cooldown by 30%",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Speed Demon",
                description="Increase movement speed by 30%",
                apply=lambda player: setattr(player, 'speed', player.speed * 1.3),
                icon="👟"
            ),
            Upgrade(
                name="HP Regen",
                description="Increase HP regen by 70%",
                apply=lambda player: setattr(player, 'hp_regen_multiplier', player.hp_regen_multiplier * 1.7),
                icon="❤️"
            ),
            Upgrade(
                name="Max HP",
                description="Increase MaxHP by 50%",
                apply=lambda player: setattr(player, 'max_health', player.max_health * 1.5),
                icon="❤️"
            ),
        ]

    def get_random_upgrades(self, count: int) -> List[Upgrade]:
        return random.sample(self.upgrades, count) 