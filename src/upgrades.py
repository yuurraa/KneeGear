from dataclasses import dataclass
from typing import Callable, List
import random
from math import ceil
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
                description="Decrease basic attack cooldown by 15%",
                apply=lambda player: setattr(player, 'shoot_cooldown', ceil(player.shoot_cooldown * 0.85)),
                icon="⚡"
            ),
            Upgrade(
                name="Heavy Bullets",
                description="Increase basic attack damage by 20%",
                apply=lambda player: setattr(player, 'basic_bullet_damage_multiplier', 
                                           ceil(player.basic_bullet_damage_multiplier * 1.2)),
                icon="💥"
            ),
            Upgrade(
                name="Swift Shot",
                description="Increase basic bullet speed by 20%",
                apply=lambda player: setattr(player, 'basic_bullet_speed_multiplier', 
                                           ceil(player.basic_bullet_speed_multiplier * 1.2)),
                icon="🚀"
            ),
            Upgrade(
                name="Special Force",
                description="Increase special attack damage by 25%",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           ceil(player.special_bullet_damage_multiplier * 1.25)),
                icon="⭐"
            ),
            Upgrade(
                name="Quick Charge",
                description="Decrease special attack cooldown by 20%",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           ceil(player.special_shot_cooldown * 0.8)),
                icon="⚡"
            ),
            Upgrade(
                name="Speed Demon",
                description="Increase movement speed by 15%",
                apply=lambda player: setattr(player, 'speed', ceil(player.speed * 1.15)),
                icon="👟"
            ),
        ]

    def get_random_upgrades(self, count: int) -> List[Upgrade]:
        return random.sample(self.upgrades, count) 