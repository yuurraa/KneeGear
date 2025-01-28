import pygame
import constants
import game_state
from player import PlayerState
from upgrades import UpgradePool

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, screen):
        color = (min(self.color[0] + 30, 255), 
                min(self.color[1] + 30, 255), 
                min(self.color[2] + 30, 255)) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, constants.BLACK, self.rect, 2)  # Border

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, constants.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class UpgradeButton(Button):
    def __init__(self, x, y, width, height, upgrade):
        super().__init__(x, y, width, height, "", constants.GREEN)
        self.upgrade = upgrade
        self.width = width
        self.height = height
            
        
    def draw(self, screen):
        super().draw(screen)
        
        # Draw upgrade name, rarity, and description
        font_name = pygame.font.Font(None, 32)
        font_desc = pygame.font.Font(None, 24)
        font_rarity = pygame.font.Font(None, 20)
        
        # Draw name with icon
        name_surface = font_name.render(f"{self.upgrade.icon} {self.upgrade.name}", True, constants.BLACK)
        name_rect = name_surface.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        screen.blit(name_surface, name_rect)
        
        # Draw rarity
        rarity_surface = font_rarity.render(self.upgrade.Rarity, True, constants.BLACK)
        rarity_rect = rarity_surface.get_rect(midtop=(self.rect.centerx, name_rect.bottom))
        screen.blit(rarity_surface, rarity_rect)
        
        # Text wrapping for description
        words = self.upgrade.description.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font_desc.render(test_line, True, constants.BLACK)
            if test_surface.get_width() <= self.width - 20:  # 10px padding on each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw wrapped description
        y_offset = rarity_rect.bottom + 5
        for line in lines:
            desc_surface = font_desc.render(line, True, constants.BLACK)
            desc_rect = desc_surface.get_rect(midtop=(self.rect.centerx, y_offset))
            screen.blit(desc_surface, desc_rect)
            y_offset += desc_surface.get_height()

def draw_level_up_menu(screen):
    # Create semi-transparent overlay
    overlay = pygame.Surface((game_state.screen_width, game_state.screen_height))
    overlay.fill(constants.BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Create menu panel
    panel_width = 1000
    panel_height = 600
    panel_x = (game_state.screen_width - panel_width) // 2
    panel_y = (game_state.screen_height - panel_height) // 2
    
    pygame.draw.rect(screen, constants.WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, constants.BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Level up text
    font = pygame.font.Font(None, 48)
    text = font.render(f"Level {game_state.player.player_level} - Choose an Upgrade", True, constants.BLACK)
    text_rect = text.get_rect(center=(game_state.screen_width // 2, panel_y + 50))
    screen.blit(text, text_rect)

    # Get random upgrades
    if not hasattr(game_state, 'current_upgrade_options'):
        upgrade_pool = UpgradePool()
        game_state.current_upgrade_options = upgrade_pool.get_random_upgrades(3, game_state.player)

    # Create upgrade buttons
    button_width = 280
    button_height = 120
    button_spacing = 40
    total_width = (button_width * 3) + (button_spacing * 2)
    start_x = (game_state.screen_width - total_width) // 2

    upgrade_buttons = []
    for i, upgrade in enumerate(game_state.current_upgrade_options):
        x = start_x + (button_width + button_spacing) * i
        y = panel_y + 200
        button = UpgradeButton(x, y, button_width, button_height, upgrade)
        button.draw(screen)
        upgrade_buttons.append(button)

    return upgrade_buttons 