import pygame
import game_state
import constants
import os

# Initialize score
score = 0
high_score = 0

# Define the directory and file for storing the high score.
DATA_DIR = "data"
HIGH_SCORE_FILE = os.path.join(DATA_DIR, "high_score.txt")

def ensure_data_directory():
    """Ensure that the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_high_score(filename=HIGH_SCORE_FILE):
    """Load the high score from a text file."""
    global high_score
    ensure_data_directory()
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                high_score = int(f.read().strip())
        except ValueError:
            # In case the file is corrupted or empty, reset to 0.
            high_score = 0
    else:
        high_score = 0

def save_high_score(filename=HIGH_SCORE_FILE):
    """Save the current high score to a text file."""
    ensure_data_directory()
    with open(filename, "w") as f:
        f.write(str(high_score))

def increase_score(amount):
    global score
    score += amount

def reset_score():
    global score
    score = 0

def update_high_score():
    """Check if the current score beats the high score.
       If so, update the high score and save it to file."""
    global high_score, score
    if score > high_score:
        high_score = score
        save_high_score()

def draw_score(screen):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, constants.BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, constants.BLACK)
    screen.blit(score_text, (20, 50))
    screen.blit(high_score_text, (20, 80))
    
def get_score():
    return score

# Load the high score when this module is imported
load_high_score()
