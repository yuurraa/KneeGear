# skins.py
import pygame
import math
import os
import src.engine.game_state as game_state

class Skin:
    def __init__(self, id, name, color, shape, rarity, frames_folder=None,
                 scale_factor_x=1.0, scale_factor_y=1.0, weapon_scale_factor_x=1.0, weapon_scale_factor_y=1.0, base_rotation=0,
                 weapon_offset_distance=0):
        self.id = id
        self.name = name
        self.color = color
        self.shape = shape
        self.rarity = rarity
        self.frames_folder = frames_folder
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 5  # Display each frame for a set number of ticks
        self.frame_counter = 0
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.weapon_scale_factor_x = weapon_scale_factor_x
        self.weapon_scale_factor_y = weapon_scale_factor_y
        self.base_rotation = base_rotation
        self.last_rotation = base_rotation
        self.animation_cycle = 0

        self.weapon_offset_distance = weapon_offset_distance
        self.weapon_frame = None

        # NEW: Projectile skin attributes (they can be None if not provided)
        self.projectile_skin_basic = None
        self.projectile_skin_special = None

        if self.frames_folder:
            self.load_frames()
            self.load_projectile_skins()

    def load_frames(self):
        # Load body frames from the "/body" folder
        body_folder = os.path.join(self.frames_folder, "body")
        frame_files = sorted(os.listdir(body_folder),
                             key=lambda f: int(''.join(filter(str.isdigit, f)))
                             if 'frame_BLINK' not in f else float('inf'))
        for frame_file in frame_files:
            frame_path = os.path.join(body_folder, frame_file)
            frame_surface = pygame.image.load(frame_path).convert_alpha()
            if "frame_BLINK" in frame_file:
                self.blink_frame = frame_surface
            else:
                self.frames.append(frame_surface)

        # Load the weapon frame from the "/weapon" folder.
        weapon_folder = os.path.join(self.frames_folder, "weapon")
        if os.path.exists(weapon_folder):
            for file in os.listdir(weapon_folder):
                if "weapon_HOLD" in file:
                    weapon_path = os.path.join(weapon_folder, file)
                    self.weapon_frame = pygame.image.load(weapon_path).convert_alpha()
                    break

    def load_projectile_skins(self):
        weapon_folder = os.path.join(self.frames_folder, "weapon")
        basic_filename = f"{self.shape}_weapon_BASIC.png"
        basic_path = os.path.join(weapon_folder, basic_filename)
        if os.path.exists(basic_path):
            base_image = pygame.image.load(basic_path).convert_alpha()
            
            if self.shape == "hoshimachi_suisei":
                from src.player.special_effects import HoshimachiProjectileSkin
                self.projectile_skin_basic = HoshimachiProjectileSkin(base_image, self.weapon_scale_factor_x, self.weapon_scale_factor_y)
                
            else:
                self.projectile_skin_basic = ProjectileSkin(basic_path, self.weapon_scale_factor_x, self.weapon_scale_factor_y)
            print("Loaded basic projectile skin:", basic_path)

        special_filename = f"{self.shape}_weapon_SPECIAL.png"
        special_path = os.path.join(weapon_folder, special_filename)
        if os.path.exists(special_path):
            base_image = pygame.image.load(special_path).convert_alpha()
            
            if self.shape == "hoshimachi_suisei":
                from src.player.special_effects import HoshimachiProjectileSkin
                self.projectile_skin_special = HoshimachiProjectileSkin(base_image, self.weapon_scale_factor_x - 7, self.weapon_scale_factor_y - 7)
                
            else:
                self.projectile_skin_special = ProjectileSkin(special_path, self.weapon_scale_factor_x - 5, self.weapon_scale_factor_y - 5)
            print("Loaded special projectile skin:", special_path)


    def draw(self, screen, x, y, size, flip=False):
        from src.player.player import PlayerState

        can_rotate = (not game_state.paused and not game_state.game_over and 
                      not game_state.showing_upgrades and not game_state.showing_stats and 
                      game_state.player.state != PlayerState.LEVELING_UP)
        if can_rotate:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - x
            dy = mouse_y - y
            angle = math.degrees(math.atan2(dy, dx))
            adjusted_angle = angle - self.base_rotation
            self.last_rotation = adjusted_angle

        scaled_width = int(size * self.scale_factor_x)
        scaled_height = int(size * self.scale_factor_y)

        if self.weapon_frame:
            scaled_weapon = pygame.transform.scale(self.weapon_frame, (scaled_width, scaled_height))
            rotated_weapon = pygame.transform.rotate(scaled_weapon, -self.last_rotation)
            theta_rad = math.radians(self.last_rotation)
            offset_x = -self.weapon_offset_distance * math.sin(theta_rad)
            offset_y = self.weapon_offset_distance * math.cos(theta_rad)
            weapon_center = (x + offset_x, y + offset_y)
            weapon_rect = rotated_weapon.get_rect(center=weapon_center)
            screen.blit(rotated_weapon, weapon_rect.topleft)

        if self.frames:
            frame_index = self.current_frame
            if frame_index == 6 and hasattr(self, 'blink_frame') and self.blink_frame:
                if self.animation_cycle % 3 == 1:
                    frame = self.blink_frame
                else:
                    frame = self.frames[frame_index]
            else:
                frame = self.frames[frame_index]

            scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
            if can_rotate:
                rotated_frame = pygame.transform.rotate(scaled_frame, -self.last_rotation)
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                    self.frame_counter = 0
                    if self.current_frame == 0:
                        self.animation_cycle += 1
            else:
                rotated_frame = pygame.transform.rotate(scaled_frame, -self.last_rotation)

            rect = rotated_frame.get_rect(center=(x, y))
            screen.blit(rotated_frame, rect.topleft)
        else:
            if self.shape == "square":
                rect = pygame.Rect(x - size / 2, y - size / 2, size, size)
                pygame.draw.rect(screen, self.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            else:
                points = []
                for i in range(5):
                    angle_rad = math.radians(90 + 72 * i)
                    px = x + size * math.cos(angle_rad)
                    py = y - size * math.sin(angle_rad)
                    points.append((px, py))
                pygame.draw.polygon(screen, self.color, points)
                
class ProjectileSkin:
    def __init__(self, image_path, weapon_scale_factor_x=1.0, weapon_scale_factor_y=1.0):
        self.base_image = pygame.image.load(image_path).convert_alpha()
        self.current_angle = 0
        self.weapon_scale_factor_x = weapon_scale_factor_x
        self.weapon_scale_factor_y = weapon_scale_factor_y

    def update(self):
        self.current_angle = (self.current_angle) % 360

    def draw(self, screen, x, y, size):
        # Scale the image to the desired size.
        scale_x = size * self.weapon_scale_factor_x
        scale_y = size * self.weapon_scale_factor_y
        scaled_image = pygame.transform.scale(self.base_image, (int(scale_x), int(scale_y)))
        rect = scaled_image.get_rect(center=(x, y))
        pygame.draw.rect(screen, (255, 0, 0), rect, 1)
        screen.blit(scaled_image, rect.topleft)
