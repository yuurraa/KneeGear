from dataclasses import dataclass
from typing import Callable, List
import random
from math import ceil, floor
from player import Player
import pygame

@dataclass
class Upgrade:
    name: str
    description: str
    Rarity: str
    apply: Callable[[Player], None]
    icon: str  # Could be used for future UI improvements
    max_level: int = 99999  # Default to infinite unless specified otherwise

class UpgradePool:
    def __init__(self):
        self.rarity_weights = {
            "Common": 60,
            "Rare": 30,
            "Epic": 10
        }
        self.icon_images = {
            "additional_projectiles": pygame.image.load("assets/icons/additional_projectiles.png"),
            "attack_damage": pygame.image.load("assets/icons/attack_damage.png"),
            "attack_cooldown": pygame.image.load("assets/icons/attack_cooldown.png"),
            "bullet_speed": pygame.image.load("assets/icons/bullet_speed.png"),
            "defence": pygame.image.load("assets/icons/defence.png"),
            "heavy": pygame.image.load("assets/icons/heavy.png"),
            "hp_pickup": pygame.image.load("assets/icons/hp_pickup.png"),
            "hp_regen": pygame.image.load("assets/icons/hp_regen.png"),
            "hp": pygame.image.load("assets/icons/hp.png"),
            "lifesteal": pygame.image.load("assets/icons/lifesteal.png"),
            "movement_speed": pygame.image.load("assets/icons/movement_speed.png"),
            "pierce": pygame.image.load("assets/icons/pierce.png"),
            "repierce": pygame.image.load("assets/icons/repierce.png"),
            "sniper": pygame.image.load("assets/icons/sniper.png"),
            "unhealthy": pygame.image.load("assets/icons/unhealthy.png"),
        }
        self.upgrades = [
            Upgrade(
                name="Basic Attack Cooldown",
                description="Decrease basic attack cooldown by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.7),
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Basic Attack Damage",
                description="Increase basic attack damage by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'basic_bullet_damage_multiplier', 
                                           player.basic_bullet_damage_multiplier * 1.4),
                icon="attack_damage"
            ),
            Upgrade(
                name="Basic Attack Additional Projectile",
                description="Adds 1 additional projectile per basic shot",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'basic_bullet_extra_projectiles_per_shot_bonus', 
                                           player.basic_bullet_extra_projectiles_per_shot_bonus + 1),
                max_level=3,
                icon="additional_projectiles"
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
                icon="sniper"
            ),
            Upgrade(
                name="Heavy Bullets",
                description=r"Increase basic attack damage by 80%, but decreases bullet speed by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.8),
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 0.7),
                ][-1],
                icon="heavy"
            ),
            Upgrade(
                name="Unhealthy Shot",
                description=r"Increase basic attack damage by 50%, and decreases cooldown by 25%, but decreases Max HP by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.5),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.75),
                    setattr(player, 'max_health', player.max_health * 0.8),
                ][-1],
                icon="unhealthy"
            ),          
            Upgrade(
                name="Bullet Speed",
                description="Increase all bullet speed by 40%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 1.4),
                    setattr(player, 'special_bullet_speed_multiplier', player.special_bullet_speed_multiplier * 1.4),
                ][-1],
                icon="bullet_speed"
            ),
            Upgrade(
                name="Basic Attack Pierce",
                description="Increase basic bullet piercing by 50%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'basic_bullet_piercing_multiplier', 
                                           player.basic_bullet_piercing_multiplier*1.5),
                icon="pierce"
            ),
            Upgrade(
                name="Damage",
                description="Increase all damage by 30%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 1.3),
                    setattr(player, 'special_bullet_damage_multiplier', player.special_bullet_damage_multiplier * 1.3),
                ][-1],
                icon="attack_damage"
            ),
            
            Upgrade(
                name="Cooldown",
                description="Decrease all cooldowns by 25%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.75),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.75),
                ][-1],
                icon="attack_cooldown"
            ),
            
            Upgrade(
                name="Special Attack Damage",
                description="Increase special attack damage by 50%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 1.5),
                icon="attack_damage"
            ),
            Upgrade(
                name="Special Attack Damage EX",
                description="Increase special attack damage by 80% but decreases basic attack damage by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 2),
                    setattr(player, 'basic_bullet_damage_multiplier', 
                                           player.basic_bullet_damage_multiplier * 0.7),
                ][-1],
                icon="attack_damage"
            ),
            Upgrade(
                name="Special Attack Cooldown",
                description="Decrease special attack cooldown by 30%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.7),
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Special Attack Cooldown EX",
                description="Decrease special attack cooldown by 40% but increases basic attack cooldown by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.5),
                    setattr(player, 'shoot_cooldown', 
                                           player.shoot_cooldown * 1.2),
                ][-1],
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Special Attack Pierce",
                description="Increase special bullet piercing by 50%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_piercing_multiplier', 
                                           player.special_bullet_piercing_multiplier * 1.5),
                icon="pierce"
            ),
            Upgrade(
                name="Repiercing Special Shot",
                description="Special bullets can pierce the same enemy multiple times",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'special_bullet_can_repierce', True),
                max_level=1,
                icon="repierce"
            ),
            Upgrade(
                name="Movement Speed",
                description="Increase movement speed by 30%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'speed', player.speed * 1.3),
                icon="movement_speed"
            ),
            Upgrade(
                name="HP Regen",
                description="Adds 0.5% to hp regen (proportion of max hp) ",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_regen_percent_bonus', player.hp_regen_percent_bonus + 0.5),
                icon="hp_regen"
            ),
            Upgrade(
                name="Max HP",
                description="Increase Max Hp by 100%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'max_health', player.max_health * 2),
                icon="hp"
            ),
            Upgrade(
                name="Hp Pickup",
                description="Adds 10% to healing from hp pickups (proportion of max hp)",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_pickup_healing_percent_bonus', player.hp_pickup_healing_percent_bonus + 10),
                icon="hp_pickup"
            ),
            Upgrade(
                name="Hp Steal",
                description="Adds 6% Hp steal to all attacks",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'hp_steal', player.hp_steal + 0.06),
                icon="lifesteal"
            ),
            Upgrade(
                name="Damage Reduction",
                description=r"Adds 10% damage reduction to all attacks",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'damage_reduction_percent_bonus', player.damage_reduction_percent_bonus + 10),
                max_level=5,
                icon="defence"
            ),
        ]

    def get_random_upgrades(self, count: int, player: Player) -> List[Upgrade]:
        selected_upgrades = []
        available_upgrades = self.upgrades.copy()
        
        # Filter out upgrades that have reached their max level
        available_upgrades = [
            upgrade for upgrade in available_upgrades 
            if player.upgrade_levels.get(upgrade.name, 0) < upgrade.max_level
        ]
        
        for _ in range(min(count, len(available_upgrades))):
            if not available_upgrades:
                break
                
            # Instead of grouping by rarity:
            weights = [self.rarity_weights[upgrade.Rarity] for upgrade in available_upgrades]
            
            # Then randomly select an upgrade of that rarity
            chosen_upgrade = random.choices(available_upgrades, weights=weights, k=1)[0]
            selected_upgrades.append(chosen_upgrade)
            
            # Remove the chosen upgrade from available pool
            available_upgrades.remove(chosen_upgrade)
            
        return selected_upgrades 