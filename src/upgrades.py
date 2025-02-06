from dataclasses import dataclass
from typing import Callable, List
import random
from math import ceil, floor
import pygame

import src.constants as constants
from src.player import Player

@dataclass
class Upgrade:
    name: str
    description: str
    Rarity: str
    apply: Callable[[Player], None]
    icon: str  # Could be used for future UI improvements
    max_level: int = 99999  # Default to infinite unless specified otherwise

    def __hash__(self):
        # Use the name as the unique identifier for hashing
        return hash(self.name)

    def __eq__(self, other):
        # Ensure equality is based on the name
        if isinstance(other, Upgrade):
            return self.name == other.name
        return False

class UpgradePool:
    def __init__(self):
        self.rarity_weights = {
            "test": 1000000,
            "Common": 60,
            "Rare": 30,
            "Epic": 10,
            "Mythic": 3,
            "Exclusive": 5000000000,
            "Legendary": 1
        }
        
        # general rules:
        # 1. general damage scaling should be 1.4x per level as the benchmark, increase or decrease based on rarity or other factors
        # 2. specialized damage scaling should be less than (general damage scaling * 2) but more than (general damage scaling * 1.5) for same rarity
        # 3. Special attack should have slightly better scaling than basic attack
        # 4. increased damage scaling from cooldown reduction should be slightly less than general damage scaling
        # 5. hp scaling should be 2x per level as the benchmark
        # 6. there should be balanced porportion bewteen hp/DR and damage scaling
        
        # Load upgrade icons
        self.icon_images = {}
        for icon_name in ["additional_projectiles", "attack_cooldown","attack_damage", "basic_distance", "bullet_speed", "cooldown_ex",
                          "damage_ex", "defence", "dmg_pickup", "extra_choice", "fat_special", "fear", "frenzy", "heavy",
                          "hp_pickup", "hp_regen", "hp", "hybrid_plus", "hybrid", "lifesteal", "more_pickup", "movement_speed",
                          "pacifist", "permanent_dmg", "permanent_hp", "pierce", "pride","rage", "repierce", "size_matters", "sniper",
                          "special_distance", "super_regen", "turtle_up", "unhealthy", "vengeful", "you_lucky_bastard"]:
            try:
                self.icon_images[icon_name] = pygame.image.load(f"assets/icons/{icon_name}.png").convert_alpha()
            except:
                print(f"Failed to load icon: {icon_name}")

        self.upgrades = [
            Upgrade(
                name="Attack Damage",
                description="Increase attack damage by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 1.4),
                icon="attack_damage"
            ),
            Upgrade(
                name="Attack Damage Plus",
                description="Increase attack damage by 45%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 1.45),
                icon="attack_damage"
            ),
            Upgrade(
                name="Attack Damage and Decreased Cooldown",
                description="Increase attack damage by 25% and decrease all cooldowns by 10%",
                Rarity="Common",
                apply=lambda player: [
                    setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 1.25),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.9),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.9),
                ][-1],
                icon="hybrid"
            ),
            Upgrade(
                name="Attack Damage and Increased Cooldown",
                description="Increase attack damage by 60% but increase all cooldowns by 10%",
                Rarity="Common",
                apply=lambda player: [
                    setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 1.6),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 1.1),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 1.1),
                ][-1],
                icon="hybrid"
            ),
            Upgrade(
                name="Attack Damage and bullet speed",
                description="Increase attack damage by 40% and increase all bullet speed by 20%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 1.4),
                    setattr(player, 'basic_bullet_speed_multiplier', 
                                           player.basic_bullet_speed_multiplier * 1.2),
                    setattr(player, 'special_bullet_speed_multiplier', 
                                           player.special_bullet_speed_multiplier * 1.2),
                ][-1],
                icon="hybrid"
            ),

            Upgrade(
                name="Cooldown",
                description="Decrease all cooldowns by 30%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.7),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.7),
                ][-1],
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Unhealthy Shot",
                description=r"Increase damage by 80%, but decreases Max HP by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'base_damage_multiplier', player.base_damage_multiplier * 1.8),
                    setattr(player, 'max_health', player.max_health * 0.8),
                ][-1],
                icon="unhealthy"
            ),
            Upgrade(
                name="Bullet Speed",
                description="Increase all bullet speed by 50%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 1.5),
                    setattr(player, 'special_bullet_speed_multiplier', player.special_bullet_speed_multiplier * 1.5),
                ][-1],
                icon="bullet_speed"
            ),       
            Upgrade(
                name="Basic Attack Damage",
                description="Increase basic attack damage by 70%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'basic_bullet_damage_multiplier', 
                                           player.basic_bullet_damage_multiplier * 1.7),
                icon="attack_damage"
            ),
            Upgrade(
                name="Basic Attack Cooldown",
                description="Decrease basic attack cooldown by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.6),
                icon="attack_cooldown"
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
                description=r"Increase basic attack damage by 160% and bullet speed by 20%, but increases basic attack cooldown by 25%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 2.6),
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 1.2),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 1.25)
                ][-1],
                icon="sniper"
            ),
            Upgrade(
                name="Heavy Bullets",
                description=r"Increase basic attack damage by 120%, but decreases basic attack bullet speed by 25%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 2.2),
                    setattr(player, 'basic_bullet_speed_multiplier', player.basic_bullet_speed_multiplier * 0.75),
                ][-1],
                icon="heavy"
            ),
            Upgrade(
                name="Basic Attack Pierce",
                description="Increase basic bullet piercing by 100%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'basic_bullet_piercing_multiplier', 
                                           player.basic_bullet_piercing_multiplier*2),
                icon="pierce"
            ),
            Upgrade(
                name="Basic Attack Distance Scaling",
                description="Basic bullets gain up to +200% damage the further they travel, but base basic damage is reduced by 25%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'basic_bullet_scales_with_distance_travelled', True),
                    setattr(player, 'basic_bullet_damage_multiplier', player.basic_bullet_damage_multiplier * 0.75),
                ][-1],
                max_level=1,
                icon="basic_distance"
            ),
            
            Upgrade(
                name="Special Attack Damage",
                description="Increase special attack damage by 80%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 1.8),
                icon="attack_damage"
            ),
            Upgrade(
                name="Special Attack Damage Plus",
                description="Increase special attack damage by 100%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_damage_multiplier', 
                                           player.special_bullet_damage_multiplier * 2),
                icon="attack_damage"
            ),
            Upgrade(
                name="Special Attack Damage EX",
                description=r"Increase special attack damage by 120% but decreases attack damage by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_bullet_damage_multiplier',     
                                           player.special_bullet_damage_multiplier * 2.2),
                    setattr(player, 'base_damage_multiplier', 
                                           player.base_damage_multiplier * 0.8),
                ][-1],
                icon="damage_ex"
            ),
            Upgrade(
                name="Special Attack Cooldown",
                description="Decrease special attack cooldown by 40%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 

                                           player.special_shot_cooldown * 0.6),
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Special Attack Cooldown Plus",
                description="Decrease special attack cooldown by 45%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.55),
                icon="attack_cooldown"
            ),
            Upgrade(
                name="Special Attack Cooldown EX",
                description="Decrease special attack cooldown by 50% but increases basic attack cooldown by 10%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_shot_cooldown', 
                                           player.special_shot_cooldown * 0.5),
                    setattr(player, 'shoot_cooldown', 
                                           player.shoot_cooldown * 1.1),
                ][-1],
                icon="cooldown_ex"
            ),
            Upgrade(
                name="Special Attack Pierce",
                description="Increase special bullet piercing by 120%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'special_bullet_piercing_multiplier', 
                                           player.special_bullet_piercing_multiplier * 2.2),
                icon="pierce"
            ),
            Upgrade(
                name="Fat Special Attack",
                description=r"Increase special attack bullet damage by 200% and radius by 25%, but increases special attack cooldown by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_bullet_damage_multiplier', player.special_bullet_damage_multiplier * 3),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 1.3),
                    setattr(player, 'special_bullet_radius_multiplier', player.special_bullet_radius_multiplier * 1.25),
                ][-1],
                max_level=4,
                icon="fat_special"
            ),
            Upgrade(
                name="Vengeful Special",
                description="Increases next special attack damage by 200% of raw damage taken, decreases special attack cooldown by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'percent_damage_taken_special_attack_bonus', player.percent_damage_taken_special_attack_bonus + 200),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.8),
                ][-1],
                max_level=1,
                icon="vengeful"
            ),
            Upgrade(
                name="Repiercing Special Attack",
                description="Special bullets can pierce the same enemy multiple times",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'special_bullet_can_repierce', True),
                max_level=1,
                icon="repierce"
            ),
            Upgrade(
                name="Special Attack Distance Scaling",
                description="Special bullets gain up to +200% damage the closer you are to the enemy, but special base damage is reduced by 25%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'special_bullet_scales_with_distance_travelled', True),
                    setattr(player, 'special_bullet_damage_multiplier', player.special_bullet_damage_multiplier * 0.75),
                ][-1],
                max_level=1,
                icon="special_distance"
            ),
            Upgrade(
                name="Movement Speed",
                description="Increase movement speed by 30%",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'speed', player.speed * 1.3),
                max_level=3,
                icon="movement_speed"
            ),
            Upgrade(
                name="HP Regen",
                description="Adds 1.5% to HP regen (proportion of max hp) ",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_regen_percent_bonus', player.hp_regen_percent_bonus + 1.5),
                icon="hp_regen"
            ),
            Upgrade(
                name="Super HP Regen",
                description="Adds 4.5% to HP regen (proportion of max HP) but decreases max HP by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'hp_regen_percent_bonus', player.hp_regen_percent_bonus + 4.5),
                    setattr(player, 'max_health', player.max_health * 0.7),
                ][-1],
                icon="super_regen"
            ),
            Upgrade(
                name="Max HP",
                description="Increase Max HP by 100%",
                Rarity="Common",
                apply=lambda player: setattr(player, 'max_health', player.max_health * 2),
                icon="hp"
            ),
            Upgrade(
                name="Max HP + Damage Reduction",
                description="Increase Max Hp by 100% and adds 10% damage reduction",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 2),
                    setattr(player, 'damage_reduction_percent_bonus', player.damage_reduction_percent_bonus + 10),
                ][-1],
                max_level=4,
                icon="hybrid",
            ),
            Upgrade(
                name="Pacifist",
                description="Increase Max Hp by 200% and adds 1.5% to hp regen, but decreases damage by 20%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 3),
                    setattr(player, 'hp_regen_percent_bonus', player.hp_regen_percent_bonus + 1.5),
                    setattr(player, 'base_damage_multiplier', player.base_damage_multiplier * 0.8),
                ][-1],
                icon="pacifist",
            ),
            Upgrade(
                name="Turtle up",
                description="Increase Max Hp by 100% and adds 20% to damage reduction, but decreases movement speed by 30%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 2),
                    setattr(player, 'damage_reduction_percent_bonus', player.damage_reduction_percent_bonus + 10),
                    setattr(player, 'speed', player.speed * 0.7),
                ][-1],
                icon="turtle_up",
            ),
            Upgrade(
                name="Pickup Healing",
                description="Adds 20% to healing from pickups (proportion of max hp)",
                Rarity="Common",
                apply=lambda player: setattr(player, 'hp_pickup_healing_percent_bonus', player.hp_pickup_healing_percent_bonus + 20),
                icon="hp_pickup",
                max_level=3,
            ),
            Upgrade(
                name="Pickup Temporary Damage Boost",
                description="Adds 15% to 20s damage boost from pickups",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'hp_pickup_damage_boost_percent_bonus', player.hp_pickup_damage_boost_percent_bonus + 15),
                icon="dmg_pickup",
                max_level=4,
            ),
            Upgrade(
                name="More pickups",
                description="1 additional pickup can be present at a time",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'max_pickups_on_screen', player.max_pickups_on_screen + 1),
                icon="more_pickup",
                max_level=1,
            ),
            Upgrade(
                name="Pickup Permanent Damage Boost",
                description="Pickups now permanently increase damage by 0.5%",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'hp_pickup_permanent_damage_boost_percent_bonus', player.hp_pickup_permanent_damage_boost_percent_bonus + 0.5),
                icon="permanent_dmg",
                max_level=1,
            ),
            Upgrade(
                name="Pickup Permanent HP Boost",
                description="Pickups now permanently increase max hp by 0.5%",
                Rarity="Epic",
                apply=lambda player: setattr(player, 'hp_pickup_permanent_hp_boost_percent_bonus', player.hp_pickup_permanent_hp_boost_percent_bonus + 0.5),
                icon="permanent_hp",
                max_level=1,
            ),
            Upgrade(
                name="Lifesteal",
                description=r"Adds 4% lifesteal to all attacks",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'hp_steal', player.hp_steal + 0.04),
                icon="lifesteal"
            ),
            Upgrade(
                name="Damage Reduction",
                description=r"Adds 20% damage reduction from all attacks",
                Rarity="Rare",
                apply=lambda player: setattr(player, 'damage_reduction_percent_bonus', player.damage_reduction_percent_bonus + 20),
                icon="defence"
            ),
            Upgrade(
                name="All Rounder",
                description=r"Increases max hp by 30%, increases damage by 20%, decreases all cooldowns by 10%",
                Rarity="Rare",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 1.3),
                    setattr(player, 'base_damage_multiplier', player.base_damage_multiplier * 1.2),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.9),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.9),
                ][-1],
                icon="hybrid"
            ),
            Upgrade(
                name="All Rounder Plus",
                description=r"Increases max hp by 40%, increases damage by 25%, decreases all cooldowns by 10%",
                Rarity="Epic",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 1.4),
                    setattr(player, 'base_damage_multiplier', player.base_damage_multiplier * 1.25),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.9),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.9),
                ][-1],
                icon="hybrid_plus"
            ),
            Upgrade(
                name="You Lucky Bastard",
                description=r"Increases max hp by 100%, Adds 10% damage reduction, increases damage by 50%, decreases all cooldowns by 20%",
                Rarity="Legendary",
                apply=lambda player: [
                    setattr(player, 'max_health', player.max_health * 2),
                    setattr(player, 'base_damage_multiplier', player.base_damage_multiplier * 1.5),
                    setattr(player, 'shoot_cooldown', player.shoot_cooldown * 0.8),
                    setattr(player, 'special_shot_cooldown', player.special_shot_cooldown * 0.8),
                    setattr(player, 'damage_reduction_percent_bonus', player.damage_reduction_percent_bonus + 10),
                ][-1],
                max_level=1,
                icon="you_lucky_bastard"
            ),
            Upgrade(
                name="Size Matters",
                description="Reduces player size by 30%, increases movement speed by 30%",
                Rarity="Mythic",
                apply=lambda player: [
                    setattr(player, 'size', floor(player.size * 0.7)),
                    setattr(player, 'speed', player.speed * 1.3),
                ][-1],
                icon="size_matters",
                max_level=1,
            ),
            Upgrade(
                name="Rage",
                description=r"+20% damage per enemy on screen",
                Rarity="Mythic",
                apply=lambda player: [
                    setattr(player, 'rage_percent_bonus', player.rage_percent_bonus + 20),
                ][-1],
                icon="rage",
                max_level=1,
            ),
            Upgrade(
                name="Fear",
                description=r"+Up to +300% damage based on how low your hp is",
                Rarity="Mythic",
                apply=lambda player: [
                    setattr(player, 'fear_percent_bonus', player.fear_percent_bonus + 300),
                ][-1],
                icon="fear",
                max_level=1,
            ),
            Upgrade(
                name="Frenzy",
                description=r"+0.5% damage per projectile on screen",
                Rarity="Mythic",
                apply=lambda player: [
                    setattr(player, 'frenzy_percent_bonus', player.frenzy_percent_bonus + 0.5),
                ][-1],
                icon="frenzy",
                max_level=1,
            ),
            Upgrade(
                name="Pride",
                description=r"Increase damage by 200% if no damage has been taken for 4 seconds",
                Rarity="Mythic",
                apply=lambda player: [
                    setattr(player, 'no_damage_buff_damage_bonus_multiplier', player.no_damage_buff_damage_bonus_multiplier + 2),
                    setattr(player, 'no_damage_buff_req_duration', 4),
                ][-1],
                icon="pride",
                max_level=1,
            ),
            # Upgrade(
            #     name="Greed",
            #     description=r"+15% xp gain",
            #     Rarity="Mythic",
            #     apply=lambda player: [
            #         setattr(player, 'xp_gain_percent_bonus', player.xp_gain_percent_bonus + 15),
            #     ][-1],
            #     icon="attack_damage",
            #     max_level=1,
            # )
            Upgrade(
                name="+1 Upgrade Choice",
                description="Gain one additional upgrade choice when leveling up",
                Rarity="Exclusive",
                apply=lambda player: None,  # The effect is handled in the menu code
                max_level=1,
                icon="extra_choice"
            ),
            Upgrade(
                name="Roll the Dice",
                description="Start with a 2% chance to gain a random upgrade when leveling up. Chance doubles on failure and resets on success.",
                Rarity="Exclusive",
                apply=lambda player: setattr(player, 'random_upgrade_chance', 0.01), # (Listed as 1% due to doubling)
                max_level=1,
                icon="extra_choice"
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
        
        def has_damage_reduction(upgrade):
            return getattr(upgrade, "damage_reduction_increase", 0) > 0

        #dont give damage reduction if player already has it maxed out
        available_upgrades = [
            upgrade for upgrade in available_upgrades
            if not (has_damage_reduction(upgrade) and player.damage_reduction_percent_bonus >= constants.player_damage_reduction_percent_cap)
        ]
        
        for _ in range(min(count, len(available_upgrades))):
            if not available_upgrades:
                break
                
            # we weight by upgrade rarity
            weights = [self.rarity_weights[upgrade.Rarity] for upgrade in available_upgrades]
            chosen_upgrade = random.choices(available_upgrades, weights=weights, k=1)[0]
            selected_upgrades.append(chosen_upgrade)
            
            # Remove the chosen upgrade from the available pool
            available_upgrades.remove(chosen_upgrade)
            
        return selected_upgrades 