import pygame
from src.engine.helpers import get_ui_scaling_factor
from src.engine.music_handler import save_music_settings
import src.engine.constants as constants

ui_scaling_factor = get_ui_scaling_factor()


class Slider:
    def __init__(self, x, y, width, height, value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value  # a float between 0 and 1
        # Define knob dimensions
        self.knob_width = 20 * ui_scaling_factor
        self.knob_height = height + 8 * ui_scaling_factor  # a little taller than the track
        # Colors (you can adjust these or pull them from constants)
        self.track_color = constants.LIGHT_GREY
        self.fill_color = constants.DARK_GREY  # Color for the filled portion
        self.knob_color = constants.WHITE
        self.dragging = False

    def draw(self, screen):
        # Define the track rectangle
        track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw the slider track (background) with a black border
        pygame.draw.rect(screen, self.track_color, track_rect)
        pygame.draw.rect(screen, constants.BLACK, track_rect, int(4 * ui_scaling_factor))  # 2-pixel black border

        # Calculate filled width based on current value
        filled_width = int(self.value * self.width)
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(screen, self.fill_color, filled_rect)
        
        # Calculate knob position (no border for the knob)
        knob_x = self.x + filled_width - self.knob_width // 2
        knob_y = self.y + (self.height - self.knob_height) // 2
        pygame.draw.rect(screen, self.knob_color, (knob_x, knob_y, self.knob_width, self.knob_height))
        pygame.draw.rect(screen, constants.BLACK, (knob_x, knob_y, self.knob_width, self.knob_height), int(4 * ui_scaling_factor))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            design_mouse_pos = pygame.mouse.get_pos()
            
            # Calculate knob's x position based on current value
            knob_x = self.x + (self.value * (self.width - self.knob_width))
            # Create knob rect
            knob_rect = pygame.Rect(
                knob_x,
                self.y + self.height // 2 - self.knob_height // 2,
                self.knob_width,
                self.knob_height
            )
            # Also create a rect for the slider track
            track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if knob_rect.collidepoint(design_mouse_pos) or track_rect.collidepoint(design_mouse_pos):
                self.dragging = True
                # Update position if clicked on track
                mouse_x = design_mouse_pos[0]
                new_knob_x = max(
                    self.x,
                    min(mouse_x - self.knob_width / 2, self.x + self.width - self.knob_width)
                )
                self.value = (new_knob_x - self.x) / (self.width - self.knob_width)
                constants.music_volume = self.value
                pygame.mixer.music.set_volume(self.value)
                save_music_settings(self.value)  # Save the new volume

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            design_mouse_pos = pygame.mouse.get_pos()
            mouse_x = design_mouse_pos[0]
            new_knob_x = max(
                self.x,
                min(mouse_x - self.knob_width / 2, self.x + self.width - self.knob_width)
            )
            self.value = (new_knob_x - self.x) / (self.width - self.knob_width)
            constants.music_volume = self.value
            pygame.mixer.music.set_volume(self.value)
            save_music_settings(self.value)  # Save the new volume