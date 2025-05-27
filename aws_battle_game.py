import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AWS Battle Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (35, 47, 62)  # AWS dark blue
ORANGE = (255, 153, 0)  # AWS orange
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Font
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 32)

# AWS services dictionary
aws_services = {
    "EC2": "Virtual servers in the cloud",
    "S3": "Scalable object storage",
    "Lambda": "Serverless compute service",
    "DynamoDB": "NoSQL database service",
    "RDS": "Relational Database Service",
    "CloudFront": "Content delivery network",
    "IAM": "Identity and Access Management",
    "VPC": "Virtual Private Cloud",
    "SNS": "Simple Notification Service",
    "SQS": "Simple Queue service"
}

# Game variables
player_x = -100  # Start off-screen
target_player_x = 100  # Final position
enemy_x = WIDTH + 100  # Start off-screen
target_enemy_x = 600  # Final position
y_position = 400
player_health = 3
enemy_health = 3
current_question = None
options = []
correct_answer = ""
game_state = "start"  # start, intro, question, player_shoot, enemy_shoot, win, lose
animation_timer = 0
bullet_pos = None
score = 0

# Load images
try:
    # Try to load custom images
    player_img = pygame.image.load('player.png')
    player_img = pygame.transform.scale(player_img, (80, 120))
    
    enemy_img = pygame.image.load('enemy.png')
    enemy_img = pygame.transform.scale(enemy_img, (80, 120))
except pygame.error:
    # Fall back to rectangles if images not found
    print("Could not load image files. Using default shapes.")
    player_img = pygame.Surface((50, 100))
    player_img.fill(GREEN)
    enemy_img = pygame.Surface((50, 100))
    enemy_img.fill(RED)

def get_new_question():
    global current_question, options, correct_answer
    
    # Select random service
    service, description = random.choice(list(aws_services.items()))
    current_question = f"What AWS service is: {description}?"
    correct_answer = service
    
    # Create options (1 correct, 3 random incorrect)
    options = [service]
    other_services = [s for s in aws_services.keys() if s != service]
    random.shuffle(other_services)
    options.extend(other_services[:3])
    random.shuffle(options)

def draw_start_screen():
    screen.fill(BLUE)
    title = large_font.render("AWS Battle Game", True, ORANGE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    instruction = font.render("Press SPACE to start", True, WHITE)
    screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, 300))

def draw_game_screen():
    screen.fill(BLUE)
    
    # Draw health bars
    pygame.draw.rect(screen, GREEN, (50, 50, player_health * 50, 20))
    pygame.draw.rect(screen, RED, (WIDTH - 50 - enemy_health * 50, 50, enemy_health * 50, 20))
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
    
    # Draw characters
    screen.blit(player_img, (player_x, y_position))
    screen.blit(enemy_img, (enemy_x, y_position))
    
    # Draw bullet if shooting
    if game_state in ["player_shoot", "enemy_shoot"] and bullet_pos:
        pygame.draw.circle(screen, ORANGE, bullet_pos, 5)
    
    # Draw question
    if game_state == "question":
        question_surface = font.render(current_question, True, WHITE)
        screen.blit(question_surface, (WIDTH//2 - question_surface.get_width()//2, 150))
        
        # Draw options
        for i, option in enumerate(options):
            option_text = font.render(f"{i+1}. {option}", True, WHITE)
            screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, 200 + i * 40))

def draw_end_screen(won):
    screen.fill(BLUE)
    if won:
        result = large_font.render("You Won!", True, GREEN)
    else:
        result = large_font.render("You Lost!", True, RED)
    
    screen.blit(result, (WIDTH//2 - result.get_width()//2, 200))
    
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 300))
    
    restart = font.render("Press SPACE to play again", True, WHITE)
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))

def handle_shooting(correct):
    global game_state, animation_timer, bullet_pos, player_health, enemy_health, score
    
    if correct:
        game_state = "player_shoot"
        bullet_pos = [player_x + 50, y_position + 50]
        animation_timer = 0
    else:
        game_state = "enemy_shoot"
        bullet_pos = [enemy_x, y_position + 50]
        animation_timer = 0

def update_intro_animation():
    global player_x, enemy_x, game_state
    
    # Move player from left
    if player_x < target_player_x:
        player_x += 5
    
    # Move enemy from right
    if enemy_x > target_enemy_x:
        enemy_x -= 5
    
    # When both characters are in position, start the question
    if player_x >= target_player_x and enemy_x <= target_enemy_x:
        game_state = "question"

def update_animation():
    global animation_timer, bullet_pos, game_state, player_health, enemy_health, score
    
    animation_timer += 1
    
    if game_state == "player_shoot":
        bullet_pos[0] += 8  # Bullet speed
        if bullet_pos[0] >= enemy_x:
            enemy_health -= 1
            score += 1
            if enemy_health <= 0:
                game_state = "win"
            else:
                get_new_question()
                game_state = "question"
    
    elif game_state == "enemy_shoot":
        bullet_pos[0] -= 8  # Bullet speed
        if bullet_pos[0] <= player_x + 50:
            player_health -= 1
            if player_health <= 0:
                game_state = "lose"
            else:
                get_new_question()
                game_state = "question"

def reset_game():
    global player_health, enemy_health, game_state, score, player_x, enemy_x, bullet_pos
    player_health = 3
    enemy_health = 3
    score = 0
    bullet_pos = None
    
    # Reset positions for entrance animation
    player_x = -100
    enemy_x = WIDTH + 100
    
    get_new_question()
    game_state = "intro"  # Start with intro animation

# Main game loop
clock = pygame.time.Clock()
get_new_question()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == "start" and event.key == pygame.K_SPACE:
                reset_game()
            
            elif game_state == "question":
                if event.key == pygame.K_1:
                    handle_shooting(options[0] == correct_answer)
                elif event.key == pygame.K_2:
                    handle_shooting(options[1] == correct_answer)
                elif event.key == pygame.K_3:
                    handle_shooting(options[2] == correct_answer)
                elif event.key == pygame.K_4:
                    handle_shooting(options[3] == correct_answer)
            
            elif game_state in ["win", "lose"] and event.key == pygame.K_SPACE:
                game_state = "start"
    
    # Update animations
    if game_state == "intro":
        update_intro_animation()
    elif game_state in ["player_shoot", "enemy_shoot"]:
        update_animation()
    
    # Draw the appropriate screen
    if game_state == "start":
        draw_start_screen()
    elif game_state in ["intro", "question", "player_shoot", "enemy_shoot"]:
        draw_game_screen()
    elif game_state == "win":
        draw_end_screen(True)
    elif game_state == "lose":
        draw_end_screen(False)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()