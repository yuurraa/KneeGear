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
    is_unique: bool = False #if true, only one of this upgrade can be applied

class UpgradePool:
    def __init__(self):
        self.rarity_weights = {
            "Common": 60,
            "Rare": 30,
            "Epic": 10
        }
        self.upgrades = [
            Upgrade(
                name="Basic Attack Cooldown",
                description="Decrease basic attack cooldown by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Basic Attack Damage",
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
                name="Bullet Speed",
                description="Increase all bullet speed by 40%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 1.4),
                    setattr(player, 'special_bullet_speed_multiplier', player.special_bullet_speed_multiplier * 1.4),
                ][-1],
                icon="🚀"
            ),
            Upgrade(
                name="Basic Attack Pierce",
                description="Increase basic bullet piercing by 1",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'basic_bullet_piercing_bonus', 
                                           player.basic_bullet_piercing_bonus + 1),
                icon="💥"
            ),
            Upgrade(
                name="Damage",
                description="Increase all damage by 30%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.3),
                    setattr(player, 'special_bullet_damage_multiplier', player.special_bullet_damage_multiplier * 1.3),
                ][-1],
                icon="💥"
            ),
            
            Upgrade(
                name="Cooldown",
                description="Decrease all cooldowns by 25%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.75),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.75),
                ][-1],
                icon="💥"
            ),
            
            Upgrade(
                name="Special Attack Damage",
                description="Increase special attack damage by 40%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 1.4),
                icon="⭐"
            ),
            Upgrade(
                name="Special Attack Cooldown",
                description="Decrease special attack cooldown by 30%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.7),
                icon="⚡"
            ),
            Upgrade(
                name="Special Attack Pierce",
                description="Increase special bullet piercing by 2",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_piercing_bonus', 
                                           player.special_bullet_piercing_bonus + 2),
                icon="⚡"
            ),
            Upgrade(
                name="Repiercing Special Shot",
                description="Special bullets can pierce the same enemy multiple times",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'special_bullet_can_repierce', True),
                is_unique=True,
                icon="⚡"
            ),
            Upgrade(
                name="Movement Speed",
                description="Increase movement speed by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'speed', player.speed * 1.3),
                icon="👟"
            ),
            Upgrade(
                name="HP Regen",
                description="Adds 0.5% to hp regen (proportion of max hp) ",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_regen_percent_bonus', player.hp_regen_percent_bonus + 0.5),
                icon="❤️"
            ),
            Upgrade(
                name="Max HP",
                description="Increase Max Hp by 100%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'max_health', player.max_health * 2),
                icon="❤️"
            ),
            Upgrade(
                name="Hp Pickup",
                description="Adds 10% to healing from hp pickups (proportion of max hp)",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_pickup_healing_percent_bonus', player.hp_pickup_healing_percent_bonus + 10),
                icon="❤️"
            ),
            Upgrade(
                name="Hp Steal",
                description="Adds 6% Hp steal to all attacks",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'hp_steal', player.hp_steal + 0.06),
                icon="⚡"
            ),
        ]

    def get_random_upgrades(self, count: int, player: Player) -> List[Upgrade]:
        selected_upgrades = []
        available_upgrades = self.upgrades.copy()
        
        # Filter out unique upgrades that player already has
        available_upgrades = [
            upgrade for upgrade in available_upgrades 
            if not (upgrade.is_unique and upgrade.name in player.applied_upgrades)
        ]
        
        for _ in range(min(count, len(available_upgrades))):
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
                
            # Get weights for valid rarities and adjust them based on available upgrades
            valid_weights = [
                self.rarity_weights[rarity] * len(upgrades_by_rarity[rarity])
                for rarity in valid_rarities
            ]
            
            # Select a rarity tier first
            chosen_rarity = random.choices(valid_rarities, weights=valid_weights, k=1)[0]
            
            # Then randomly select an upgrade of that rarity
            chosen_upgrade = random.choice(upgrades_by_rarity[chosen_rarity])
            selected_upgrades.append(chosen_upgrade)
            
            # Remove the chosen upgrade from available pool
            available_upgrades.remove(chosen_upgrade)
            
        return selected_upgrades 