from dataclasses import dataclass
from typing import Callable, List
import random
from math import ceil, floor
from player import Player

@dataclass
class Upgrade:
    name: str
    description: str
    Rarity: str
    apply: Callable[[Player], None]
    icon: str  # Could be used for future UI improvements

class UpgradePool:
    def __init__(self):
        self.rarity_weights = {
            "Common": 60,
            "Rare": 30,
            "Epic": 10
        }
        self.upgrades = [
            Upgrade(
                name="Rapid Fire",
                description="Decrease basic attack cooldown by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Sharp Bullets",
                description="Increase basic attack damage by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'basic_bullet_damage_multiplier', 
                                           player.basic_bullet_damage_multiplier * 1.4),
                icon="💥"
            ),
            Upgrade(
                name="Sniper Bullets",
                description=r"Increase basic attack damage by 80% and bullet speed by 20%, but increases cooldown by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.8),
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 1.2),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 1.2)
                ][-1],
                icon="💥"
            ),
            Upgrade(
                name="Heavy Bullets",
                description=r"Increase basic attack damage by 80%, but decreases bullet speed by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.8),
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 0.7),
                ][-1],
                icon="💥"
            ),
            
            Upgrade(
                name="Swift Shot",
                description="Increase basic bullet speed by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'basic_bullet_speed_multiplier', 
                                           player.basic_bullet_speed_multiplier * 1.4),
                icon="🚀"
            ),
            Upgrade(
                name="Piercing Shot",
                description="Increase basic bullet piercing by 1",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'basic_bullet_piercing_bonus', 
                                           player.basic_bullet_piercing_bonus + 1),
                icon="💥"
            ),
            Upgrade(
                name="Special Force",
                description="Increase special attack damage by 40%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 1.4),
                icon="⭐"
            ),
            Upgrade(
                name="Quick Charge",
                description="Decrease special attack cooldown by 30%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Speed Demon",
                description="Increase movement speed by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'speed', player.speed * 1.3),
                icon="👟"
            ),
            Upgrade(
                name="HP Regen",
                description="Increase HP regen by 70%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'hp_regen_multiplier', player.hp_regen_multiplier * 1.7),
                icon="❤️"
            ),
            Upgrade(
                name="Max HP",
                description="Increase MaxHP by 50%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'max_health', player.max_health * 1.5),
                icon="❤️"
            ),
        ]

    def get_random_upgrades(self, count: int) -> List[Upgrade]:
        selected_upgrades = []
        available_upgrades = self.upgrades.copy()
        
        for _ in range(min(count, len(self.upgrades))):
            if not available_upgrades:
                break
                
            # Group remaining upgrades by rarity
            upgrades_by_rarity = {
                "Common": [],
                "Rare": [],
                "Epic": []
            }
            
            for upgrade in available_upgrades:
                upgrades_by_rarity[upgrade.Rarity].append(upgrade)
            
            # Filter out empty rarity tiers
            valid_rarities = [rarity for rarity, upgrades in upgrades_by_rarity.items() if upgrades]
            if not valid_rarities:
                break
                
            # Get weights for valid rarities
            valid_weights = [self.rarity_weights[rarity] for rarity in valid_rarities]
            
            # Select a rarity tier first
            chosen_rarity = random.choices(valid_rarities, weights=valid_weights, k=1)[0]
            
            # Then randomly select an upgrade of that rarity
            chosen_upgrade = random.choice(upgrades_by_rarity[chosen_rarity])
            selected_upgrades.append(chosen_upgrade)
            
            # Remove the chosen upgrade from available pool
            available_upgrades.remove(chosen_upgrade)
            
        return selected_upgrades 