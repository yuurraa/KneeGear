import pygame
import game_state
import constants

# Initialize score
score = 0
high_score = 0

def increase_score(amount):
    global score
    score += amount

def reset_score():
    global score
    score = 0

def update_high_score():
    global high_score, score
    if score > high_score:
        high_score = score

def draw_score(screen):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, constants.BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, constants.BLACK)
    screen.blit(score_text, (20, 50))
    screen.blit(high_score_text, (20, 80))

