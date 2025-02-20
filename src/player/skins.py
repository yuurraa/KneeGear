import pygame
import math
import os
import src.engine.game_state as game_state

class Skin:
    def __init__(self, id, name, color, shape, rarity, frames_folder=None,
                 scale_factor_x=1.0, scale_factor_y=1.0, base_rotation=0):
        self.id = id
        self.name = name
        self.color = color
        self.shape = shape
        self.rarity = rarity
        self.frames_folder = frames_folder
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 5  # Display each frame 4 ticks
        self.frame_counter = 0
        self.scale_factor_x = scale_factor_x  # Horizontal scaling
        self.scale_factor_y = scale_factor_y  # Vertical scaling
        self.base_rotation = base_rotation  # Additional rotation offset
        self.last_rotation = base_rotation
        self.animation_cycle = 0  # NEW: Track full animation cycles

        if self.frames_folder:
            self.load_frames()


    def load_frames(self):
        frame_files = sorted(os.listdir(self.frames_folder), key=lambda f: int(''.join(filter(str.isdigit, f))) if 'frame_BLINK' not in f else float('inf'))
        for frame_file in frame_files:
            frame_path = os.path.join(self.frames_folder, frame_file)
            frame_surface = pygame.image.load(frame_path).convert_alpha()
            
            if "frame_BLINK" in frame_file:
                self.blink_frame = frame_surface  # Store blink frame separately
            else:
                self.frames.append(frame_surface)

    def draw(self, screen, x, y, size, flip=False):
        from src.player.player import PlayerState
        if self.frames:
            # Determine current frame
            frame_index = self.current_frame

            # Check if it's time to replace frame_7 with frame_BLINK
            if frame_index == 6 and hasattr(self, 'blink_frame') and self.blink_frame:
                # Use our persistent animation_cycle counter to alternate every other full cycle.
                if self.animation_cycle % 3 == 1:  
                    frame = self.blink_frame  # Swap frame_7 with blink frame on odd cycles
                else:
                    frame = self.frames[frame_index]  # Use normal frame_7 on even cycles
            else:
                frame = self.frames[frame_index]

            # Scale the frame
            scaled_width = int(size * self.scale_factor_x)
            scaled_height = int(size * self.scale_factor_y)
            scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
            
            # Handle rotation logic (same as before)
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
                rotated_frame = pygame.transform.rotate(scaled_frame, -adjusted_angle)

                # Handle animation frame updating
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                    self.frame_counter = 0
                    # When the animation loops back to the first frame, increment the cycle counter.
                    if self.current_frame == 0:
                        self.animation_cycle += 1
            else:
                rotated_frame = pygame.transform.rotate(scaled_frame, -self.last_rotation)

            # Center the rotated image on (x, y)
            rect = rotated_frame.get_rect(center=(x, y))
            screen.blit(rotated_frame, rect.topleft)
        else:
            # Fallback drawing if no frames exist.
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
