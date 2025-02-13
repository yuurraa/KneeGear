import pygame
import math
import os
import src.game_state as game_state

class Skin:
    def __init__(self, name, color, shape, rarity, frames_folder=None,
                 scale_factor_x=1.0, scale_factor_y=1.0):
        self.name = name
        self.color = color
        self.shape = shape
        self.rarity = rarity
        self.frames_folder = frames_folder
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 4  # Display each frame 4 ticks
        self.frame_counter = 0
        self.scale_factor_x = scale_factor_x  # Horizontal scaling
        self.scale_factor_y = scale_factor_y  # Vertical scaling

        if self.frames_folder:
            self.load_frames()

    def load_frames(self):
        frame_files = sorted(os.listdir(self.frames_folder))
        for frame_file in frame_files:
            frame_path = os.path.join(self.frames_folder, frame_file)
            frame_surface = pygame.image.load(frame_path).convert_alpha()
            self.frames.append(frame_surface)

    def draw(self, screen, x, y, size, flip=False):
        # If frames exist, animate the skin
        if self.frames:
            frame = self.frames[self.current_frame]
            # Use independent horizontal/vertical scaling factors
            scaled_width = int(size * self.scale_factor_x)
            scaled_height = int(size * self.scale_factor_y)
            scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
            if flip:
                scaled_frame = pygame.transform.flip(scaled_frame, True, False)
            # Center the scaled frame on (x, y)
            screen.blit(scaled_frame, (x - scaled_width / 2, y - scaled_height / 2))
            # Update animation frame (each frame shows for frame_delay ticks)
            from src.player import PlayerState
            if not game_state.paused and not game_state.game_over and not game_state.showing_upgrades and not game_state.showing_stats and game_state.player.state != PlayerState.LEVELING_UP:
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                    self.frame_counter = 0
        else:
            # No frames available – fallback drawing based on shape
            if self.shape == "square":
                rect = pygame.Rect(x - size / 2, y - size / 2, size, size)
                pygame.draw.rect(screen, self.color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Draw black border with a width of 2 pixels
            else:
                # Fallback: draw a static pentagon
                points = []
                for i in range(5):
                    angle = math.radians(90 + 72 * i)
                    px = x + size * math.cos(angle)
                    py = y - size * math.sin(angle)
                    points.append((px, py))
                pygame.draw.polygon(screen, self.color, points)
