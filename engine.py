import pygame
import random
import math

# Initialization and Constants
pygame.init()
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
PURPLE = (128, 0, 128)
TRANSLUCENT_GREEN = (0, 255, 0, 128)
TRANSLUCENT_RED = (255, 0, 0, 128)

# Game Settings
player_health = 100
player_speed = 4.5
player_bullet_speed = 6
shoot_cooldown = 0.4
special_shot_cooldown = 5
last_special_shot_time = 0

# ENEMIES
enemy_speed = 3
tank_speed = 1.5  # Slower tank movement
enemy_homing_bullet_speed = 5
enemy_aoe_bullet_speed = 7
tank_pellet_speed_range = (5, 10)  # Random speed for each pellet
max_turn_angle = 1.6  # Degrees
enemy_spawn_interval = 6
enemy_homing_interval = 1
enemy_aoe_interval = 5
tank_shotgun_interval = 4  # Time between tank shots

# Game State
enemies = []
hearts = []
projectiles = []
enemy_bullets = []
enemy_aoe_bullets = []
tank_pellets = []  # New list for tank pellets
fade_alpha = 0
game_over = False
last_shot_time = 0
last_enemy_spawn_time = 0

# Helper Functions
def calculate_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def reset_game():
    global player_health, enemies, projectiles, enemy_bullets, enemy_aoe_bullets, hearts, fade_alpha, game_over
    player_health = 100
    enemies.clear()
    projectiles.clear()
    enemy_bullets.clear()
    enemy_aoe_bullets.clear()
    hearts.clear()
    fade_alpha = 0
    game_over = False

# Drawing Functions
def draw_player(x, y, angle):
    pygame.draw.rect(screen, BLACK, (x - 16, y - 16, 22, 22))  # Outline
    pygame.draw.rect(screen, GREEN, (x - 15, y - 15, 20, 20))
    arrow_length = 20
    arrow_x = x + arrow_length * math.cos(math.radians(angle))
    arrow_y = y + arrow_length * math.sin(math.radians(angle))
    pygame.draw.line(screen, BLUE, (x, y), (arrow_x, arrow_y), 3)

def draw_enemy(x, y, health, enemy_type):
    if enemy_type == "tank":
        pygame.draw.rect(screen, BLACK, (x - 26, y - 26, 52, 52))  # Larger outline
        pygame.draw.rect(screen, (139, 69, 19), (x - 25, y - 25, 50, 50))  # Brown color
    else:
        pygame.draw.rect(screen, BLACK, (x - 21, y - 21, 42, 42))  # Regular outline
        pygame.draw.rect(screen, RED, (x - 20, y - 20, 40, 40))
    
    max_health = 400 if enemy_type == "tank" else 100
    draw_health_bar(x - 25, y - 35, health, max_health, TRANSLUCENT_RED, 
                   bar_width=50 if enemy_type == "tank" else 40, bar_height=5)

def draw_health_bar(x, y, health, max_health, color, bar_width=100, bar_height=10):
    filled_width = int((health / max_health) * bar_width)
    surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    pygame.draw.rect(surface, BLACK, (0, 0, bar_width, bar_height))
    pygame.draw.rect(surface, color, (0, 0, filled_width, bar_height))
    screen.blit(surface, (x, y))

def draw_fade_overlay():
    global fade_alpha
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.set_alpha(fade_alpha)
    fade_surface.fill(BLACK)
    screen.blit(fade_surface, (0, 0))

# Game Logic Functions
def handle_player_movement(keys, x, y):
    if keys[pygame.K_w]:
        y -= player_speed
    if keys[pygame.K_s]:
        y += player_speed
    if keys[pygame.K_a]:
        x -= player_speed
    if keys[pygame.K_d]:
        x += player_speed
        
    # Restrict player to screen boundaries
    x = max(15, min(x, screen_width - 15))
    y = max(15, min(y, screen_height - 15))

    return x, y

def move_enemy(enemy, target_x, target_y):
    speed = tank_speed if enemy["type"] == "tank" else enemy_speed
    angle = math.radians(calculate_angle(enemy["x"], enemy["y"], target_x, target_y))
    enemy["x"] += speed * math.cos(angle)
    enemy["y"] += speed * math.sin(angle)
    
    # Restrict enemies to screen boundaries
    enemy["x"] = max(20, min(enemy["x"], screen_width - 20))
    enemy["y"] = max(20, min(enemy["y"], screen_height - 20))

def update_projectiles():
    global projectiles, enemies
    for bullet in projectiles[:]:
        # Regular bullet movement
        if len(bullet) <= 3 or bullet[3] != "special":  # Regular bullet
            bullet[0] += player_bullet_speed * math.cos(math.radians(bullet[2]))
            bullet[1] += player_bullet_speed * math.sin(math.radians(bullet[2]))

        # Special shot movement (faster, more damage, and piercing)
        if len(bullet) > 3 and bullet[3] == "special":  # Special shot
            bullet[0] += player_bullet_speed * 2 * math.cos(math.radians(bullet[2]))  # Faster speed
            bullet[1] += player_bullet_speed * 2 * math.sin(math.radians(bullet[2]))  # Faster speed

        hit_enemy = False  # Flag to check if a bullet hits any enemy

        # Check collision with enemies (Special bullets pass through all enemies)
        for enemy in enemies[:]:
            if enemy["health"] > 0 and pygame.Rect(bullet[0] - 10, bullet[1] - 10, 20, 20).colliderect(enemy["x"] - 20, enemy["y"] - 20, 40, 40):
                if len(bullet) > 3 and bullet[3] == "special":  # Special bullet
                    enemy["health"] -= 20  # More damage for special bullets
                else:  # Regular bullet
                    enemy["health"] -= 10  # Regular bullet damage
                    hit_enemy = True  # Regular bullets hit and should be removed after first enemy hit
                if enemy["health"] <= 0:
                    enemies.remove(enemy)

        # Remove regular bullets after they hit an enemy (they should not pierce)
        if hit_enemy and (len(bullet) <= 3 or bullet[3] != "special"):  # Only regular bullets hit and stop
            projectiles.remove(bullet)

        # Remove bullets outside screen
        if bullet[0] < 0 or bullet[0] > screen_width or bullet[1] < 0 or bullet[1] > screen_height:
            projectiles.remove(bullet)

def update_enemy_bullets():
    global enemy_bullets, player_health
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    
    for bullet in enemy_bullets[:]:
        # Calculate time since homing started
        time_since_homing = current_time - bullet[3]
        
        # If the bullet is within the 1-second homing period, adjust its direction
        if time_since_homing < 1:
            # Calculate the angle from the bullet to the player (homing)
            angle_to_player = calculate_angle(bullet[0], bullet[1], player_x, player_y)
            
            # Calculate the angle difference between the current direction and the angle to the player
            angle_diff = angle_to_player - bullet[2]
            
            # Normalize the angle difference to the range [-180, 180]
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
                
            # Limit the angle difference to the maximum turn angle
            if abs(angle_diff) > max_turn_angle:
                angle_diff = max_turn_angle if angle_diff > 0 else -max_turn_angle
                
            # Update the bullet's angle based on the limited turn angle
            bullet[2] += angle_diff
        else:
            # After 1 second, the bullet stops homing and continues in its original direction
            angle_to_player = bullet[2]
        
        # Update bullet position in the direction of the calculated angle
        bullet[0] += enemy_homing_bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += enemy_homing_bullet_speed * math.sin(math.radians(bullet[2]))
        
        # Check collision with player
        if pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10).colliderect(player_x - 15, player_y - 15, 30, 30):
            player_health -= 10
            enemy_bullets.remove(bullet)

        # Remove bullets outside screen
        if bullet[0] < 0 or bullet[0] > screen_width or bullet[1] < 0 or bullet[1] > screen_height:
            enemy_bullets.remove(bullet)
            
def draw_projectiles():
    for bullet in projectiles:
        if len(bullet) > 3 and bullet[3] == "special":  # Special bullet
            pygame.draw.circle(screen, (255, 165, 0, 128), (int(bullet[0]), int(bullet[1])), 20)  # Larger size (radius 20)
        else:  # Regular bullet
            pygame.draw.circle(screen, BLUE, (int(bullet[0]), int(bullet[1])), 5)  # Regular bullet size (radius 5)


def update_enemy_aoe_bullets():
    global enemy_aoe_bullets, player_health
    for bullet in enemy_aoe_bullets[:]:
        bullet[0] += enemy_aoe_bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] += enemy_aoe_bullet_speed * math.sin(math.radians(bullet[2]))

        # Check collision with player
        if pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10).colliderect(player_x - 15, player_y - 15, 30, 30):
            player_health -= 5
            enemy_aoe_bullets.remove(bullet)

        # Remove bullets outside screen
        if bullet[0] < 0 or bullet[0] > screen_width or bullet[1] < 0 or bullet[1] > screen_height:
            enemy_aoe_bullets.remove(bullet)

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, screen_width)
        y = -20
    elif side == "bottom":
        x = random.randint(0, screen_width)
        y = screen_height + 20
    elif side == "left":
        x = -20
        y = random.randint(0, screen_height)
    else:  # "right"
        x = screen_width + 20
        y = random.randint(0, screen_height)

    # 20% chance to spawn a tank
    if random.random() < 0.5:
        enemies.append({
            "x": x, "y": y, 
            "health": 400, 
            "last_shot_time": 0, 
            "last_aoe_time": 0,
            "type": "tank",
            "last_shotgun_time": 0
        })
    else:
        enemies.append({
            "x": x, "y": y, 
            "health": 100, 
            "last_shot_time": 0, 
            "last_aoe_time": 0,
            "type": "regular"
        })

def enemy_homing_shoot(enemy, target_x, target_y):
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    if current_time - enemy["last_shot_time"] >= enemy_homing_interval:
        angle = calculate_angle(enemy["x"], enemy["y"], target_x, target_y)
        # Include homing start time as the 4th element in the bullet list
        enemy_bullets.append([enemy["x"], enemy["y"], angle, current_time])  # Add homing start time here
        enemy["last_shot_time"] = current_time


def enemy_aoe_shoot(enemy):
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    if current_time - enemy["last_aoe_time"] >= enemy_aoe_interval:
        for angle in range(0, 360, 45):  # Shoot bullets in a circle
            enemy_aoe_bullets.append([enemy["x"], enemy["y"], angle])
        enemy["last_aoe_time"] = current_time

def tank_shotgun(enemy, target_x, target_y):
    current_time = pygame.time.get_ticks() / 1000
    if current_time - enemy.get("last_shotgun_time", 0) >= tank_shotgun_interval:
        base_angle = calculate_angle(enemy["x"], enemy["y"], target_x, target_y)
        spread = 30  # Degrees of spread for the shotgun
        
        # Fire 20 pellets in a spread pattern
        for _ in range(20):
            angle = base_angle + random.uniform(-spread, spread)
            speed = random.uniform(tank_pellet_speed_range[0], tank_pellet_speed_range[1])
            tank_pellets.append([enemy["x"], enemy["y"], angle, speed])
        
        enemy["last_shotgun_time"] = current_time

def update_tank_pellets():
    global tank_pellets, player_health
    for pellet in tank_pellets[:]:
        # Move pellet
        pellet[0] += pellet[3] * math.cos(math.radians(pellet[2]))
        pellet[1] += pellet[3] * math.sin(math.radians(pellet[2]))
        
        # Check collision with player
        if pygame.Rect(pellet[0] - 3, pellet[1] - 3, 6, 6).colliderect(player_x - 15, player_y - 15, 30, 30):
            player_health -= 3  # Low damage per pellet
            tank_pellets.remove(pellet)
            continue
            
        # Remove pellets outside screen
        if (pellet[0] < 0 or pellet[0] > screen_width or 
            pellet[1] < 0 or pellet[1] > screen_height):
            tank_pellets.remove(pellet)

def spawn_heart():
    if len(hearts) < 1:
        hearts.append([random.randint(20, screen_width - 20), random.randint(20, screen_height - 20)])

def update_hearts():
    global hearts, player_health
    for heart in hearts[:]:
        if pygame.Rect(heart[0] - 10, heart[1] - 10, 20, 20).colliderect(player_x - 15, player_y - 15, 30, 30):
            player_health = min(player_health + 20, 100)
            hearts.remove(heart)

# Event Handling
def handle_input():
    global projectiles, last_shot_time, last_special_shot_time
    keys = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()

    # Handle player shooting with cooldown (Left-click)
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    if mouse_pressed[0] and not game_over and (current_time - last_shot_time >= shoot_cooldown):
        mx, my = pygame.mouse.get_pos()
        angle = calculate_angle(player_x, player_y, mx, my)
        projectiles.append([player_x, player_y, angle])  # Regular bullet
        last_shot_time = current_time

    # Handle player right-click shooting with cooldown (Right-click, special)
    if mouse_pressed[2] and not game_over and (current_time - last_special_shot_time >= special_shot_cooldown):
        mx, my = pygame.mouse.get_pos()
        angle = calculate_angle(player_x, player_y, mx, my)
        projectiles.append([player_x, player_y, angle, "special"])  # Special bullet
        last_special_shot_time = current_time

    return keys

# Game Loopdw
player_x, player_y = screen_width // 2, screen_height // 2
player_angle = 0
first_enemy_spawned = False
running = True

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_over:
            reset_game()

    # Handle Input
    keys = handle_input()
    player_x, player_y = handle_player_movement(keys, player_x, player_y)

    # Update player angle
    mx, my = pygame.mouse.get_pos()
    player_angle = calculate_angle(player_x, player_y, mx, my)

    # Update Game Logic
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    if not first_enemy_spawned and current_time >= 1:
        spawn_enemy()
        first_enemy_spawned = True
        last_enemy_spawn_time = current_time
    elif first_enemy_spawned and current_time - last_enemy_spawn_time >= enemy_spawn_interval:
        spawn_enemy()
        last_enemy_spawn_time = current_time
    
    def update_enemies():
        global enemies
        for enemy in enemies[:]:
            move_enemy(enemy, player_x, player_y)
            if enemy["type"] == "tank":
                tank_shotgun(enemy, player_x, player_y)
            else:
                enemy_homing_shoot(enemy, player_x, player_y)
                enemy_aoe_shoot(enemy)
            
            if enemy["health"] <= 0:
                enemies.remove(enemy)
    
    update_enemies()
    update_projectiles()
    update_enemy_bullets()
    update_enemy_aoe_bullets()
    update_tank_pellets()
    spawn_heart()
    update_hearts()
    draw_projectiles()

    # Draw Elements
    draw_player(player_x, player_y, player_angle)
    for enemy in enemies:
        draw_enemy(enemy["x"], enemy["y"], enemy["health"], enemy["type"])
    for bullet in projectiles:
        pygame.draw.circle(screen, BLUE, (int(bullet[0]), int(bullet[1])), 5)
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), 5)
    for bullet in enemy_aoe_bullets:
        pygame.draw.circle(screen, PURPLE, (int(bullet[0]), int(bullet[1])), 5)
    for heart in hearts:
        pygame.draw.circle(screen, PINK, (heart[0], heart[1]), 10)
    for pellet in tank_pellets:
        pygame.draw.circle(screen, (139, 69, 19), (int(pellet[0]), int(pellet[1])), 3)
        
    draw_health_bar(20, 20, player_health, 100, TRANSLUCENT_GREEN)

    # Game Over Fade
    if game_over:
        fade_alpha = min(fade_alpha + 5, 255)
        draw_fade_overlay()
    if player_health <= 0:
        game_over = True

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
