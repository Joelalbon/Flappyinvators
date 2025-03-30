import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game properties
BIRD_WIDTH = 40
BIRD_HEIGHT = 40
GRAVITY = 0.5
JUMP_STRENGTH = -8
ENEMY_SPEED = 3
ENEMY_SPAWN_RATE = 60
POOP_SPAWN_RATE = 120  # Frames between poop spawns
BONUS_POINTS = 50  # Points for collecting poop

# Initialize the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Emojis")
clock = pygame.time.Clock()

# Load emoji font
try:
    font = pygame.font.SysFont('segoeuiemoji', 36)
    big_font = pygame.font.SysFont('segoeuiemoji', 40)
    game_font = pygame.font.Font(None, 36)  # Regular font for score and game over
except:
    print("Emoji font not found, using regular font")
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 40)
    game_font = font

class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity_y = 0
        self.velocity_x = 0
        self.speed = 5  # Horizontal movement speed
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)
        self.score = 0
        self.bullets = []
        self.emoji = "🐦"  # Bird emoji

    def jump(self):
        self.velocity_y = JUMP_STRENGTH

    def move_horizontal(self, direction):
        self.velocity_x = direction * self.speed

    def shoot(self):
        bullet = {"rect": pygame.Rect(self.x + BIRD_WIDTH, self.y + BIRD_HEIGHT//2, 20, 20),
                 "emoji": "💨"}  # Wind emoji for bullets
        self.bullets.append(bullet)

    def update(self):
        # Vertical movement with gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Horizontal movement
        self.x += self.velocity_x
        
        # Keep bird within screen bounds
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y > HEIGHT - BIRD_HEIGHT:
            self.y = HEIGHT - BIRD_HEIGHT
            self.velocity_y = 0
            
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - BIRD_WIDTH:
            self.x = WIDTH - BIRD_WIDTH
        
        self.rect.x = self.x
        self.rect.y = self.y

        for bullet in self.bullets[:]:
            bullet["rect"].x += 7
            if bullet["rect"].x > WIDTH:
                self.bullets.remove(bullet)

    def draw(self, screen):
        bird_text = font.render(self.emoji, True, WHITE)
        screen.blit(bird_text, (self.x, self.y))
        
        for bullet in self.bullets:
            bullet_text = font.render(bullet["emoji"], True, WHITE)
            screen.blit(bullet_text, bullet["rect"])

class Enemy:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(0, HEIGHT - BIRD_HEIGHT)
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)
        self.emoji = random.choice(["👾", "👻", "👽", "🤖"])  # Random enemy emoji

    def update(self):
        self.x -= ENEMY_SPEED
        self.rect.x = self.x

    def draw(self, screen):
        enemy_text = font.render(self.emoji, True, WHITE)
        screen.blit(enemy_text, (self.x, self.y))

class Poop:
    def __init__(self):
        self.x = random.randint(WIDTH//2, WIDTH-40)
        self.y = random.randint(0, HEIGHT-40)
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)
        self.emoji = "💩"  # Poop emoji

    def draw(self, screen):
        poop_text = font.render(self.emoji, True, WHITE)
        screen.blit(poop_text, (self.x, self.y))

def main():
    bird = Bird()
    enemies = []
    poops = []
    enemy_timer = 0
    poop_timer = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.jump()
                if event.key == pygame.K_RETURN and game_over:
                    bird = Bird()
                    enemies = []
                    poops = []
                    enemy_timer = 0
                    poop_timer = 0
                    game_over = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                bird.shoot()

        if not game_over:
            # Handle continuous keyboard input for horizontal movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                bird.move_horizontal(-1)
            elif keys[pygame.K_RIGHT]:
                bird.move_horizontal(1)
            else:
                bird.move_horizontal(0)

            bird.update()

            # Spawn enemies
            enemy_timer += 1
            if enemy_timer >= ENEMY_SPAWN_RATE:
                enemies.append(Enemy())
                enemy_timer = 0

            # Spawn poop
            poop_timer += 1
            if poop_timer >= POOP_SPAWN_RATE:
                poops.append(Poop())
                poop_timer = 0

            # Update enemies
            for enemy in enemies[:]:
                enemy.update()
                if enemy.x + BIRD_WIDTH < 0:
                    enemies.remove(enemy)
                if enemy.rect.colliderect(bird.rect):
                    game_over = True
                for bullet in bird.bullets[:]:
                    if bullet["rect"].colliderect(enemy.rect):
                        enemies.remove(enemy)
                        bird.bullets.remove(bullet)
                        bird.score += 10
                        break

            # Check poop collection
            for poop in poops[:]:
                if bird.rect.colliderect(poop.rect):
                    poops.remove(poop)
                    bird.score += BONUS_POINTS

        # Draw everything
        screen.fill(BLACK)
        bird.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for poop in poops:
            poop.draw(screen)

        # Draw score
        score_text = game_font.render(f"Score: {bird.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = big_font.render("Game Over! Press ENTER to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
