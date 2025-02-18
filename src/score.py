import pygame
import os
import hashlib
from src.helpers import get_text_scaling_factor
import src.game_state as game_state
import src.constants as constants

# Initialize score
score = 0
high_score = 0

# Define the directory and file for storing the high score.

DATA_DIR = "data"
HIGH_SCORE_FILE = os.path.join(DATA_DIR, "high_score.txt")
SECRET_KEY = "my_secret_key"  # Used for hashing

def ensure_data_directory():
    """Ensure that the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def hash_score(score):
    """Generate a SHA-256 hash for the score using a secret key."""
    return hashlib.sha256(f"{score}{SECRET_KEY}".encode()).hexdigest()

def load_high_score(filename=HIGH_SCORE_FILE):
    """Load the high score from a text file and verify integrity."""
    global high_score
    ensure_data_directory()
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
                if len(lines) != 2:
                    raise ValueError("Invalid file format")
                
                stored_score = int(lines[0].strip())
                stored_hash = lines[1].strip()
                
                if stored_hash == hash_score(stored_score):
                    high_score = stored_score
                else:
                    print("Warning: High score file was tampered with! Resetting to 0.")
                    high_score = 0
        except (ValueError, IndexError):
            # In case the file is corrupted or empty, reset to 0.
            high_score = 0
    else:
        high_score = 0

def save_high_score(filename=HIGH_SCORE_FILE):
    """Save the current high score to a text file with a hash."""
    ensure_data_directory()
    with open(filename, "w") as f:
        f.write(f"{high_score}\n{hash_score(high_score)}")

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
    font = pygame.font.Font(None, get_text_scaling_factor(36))
    score_text = font.render(f"Score: {score}", True, constants.BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, constants.BLACK)
    screen.blit(score_text, (20, 55))
    screen.blit(high_score_text, (20, 85))
    
def get_score():
    return score

# Load the high score when this module is imported
load_high_score()
