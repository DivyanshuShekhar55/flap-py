import pygame
import random
import json
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIPE_WIDTH = 50
PIPE_SPEED = 5
BIRD_HEIGHT_PERCENT_TO_SCREEN = 0.05
BIRD_X_POS = SCREEN_WIDTH // 4
BIRD_Y_POS = SCREEN_HEIGHT // 2

# Colors
WHITE = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Pygame")

# Load images
bird_image = pygame.image.load('./assests/redbird-upflap.png').convert_alpha()
pipe_image = pygame.image.load('./assests/pipe-green.png').convert_alpha()
base_image = pygame.image.load('./assests/base.png').convert_alpha()

# Scale images
bird_image = pygame.transform.scale(bird_image, (50, int(SCREEN_HEIGHT * BIRD_HEIGHT_PERCENT_TO_SCREEN)))
pipe_image = pygame.transform.scale(pipe_image, (PIPE_WIDTH, SCREEN_HEIGHT))
base_image = pygame.transform.scale(base_image, (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.1)))

# Bird class
class Bird:
    def __init__(self):
        self.x = BIRD_X_POS
        self.y = BIRD_Y_POS

    def update(self):
        try:
            with open('face_y.json', 'r') as f:
                data = json.load(f)
                self.y = data['y']
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # If file doesn't exist or is invalid, don't update

    def draw(self, screen):
        screen.blit(bird_image, (self.x, self.y))

# Pipe class
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(int(SCREEN_HEIGHT * 0.2), int(SCREEN_HEIGHT * 0.6))

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Draw top pipe
        screen.blit(pipe_image, (self.x, self.height - SCREEN_HEIGHT))
        # Draw bottom pipe
        screen.blit(pipe_image, (self.x, self.height + int(3 * BIRD_HEIGHT_PERCENT_TO_SCREEN * SCREEN_HEIGHT)))

    def is_offscreen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        within_pipe_x_bounds = bird.x + 50 >= self.x and bird.x <= self.x + PIPE_WIDTH
        within_top_pipe_y_bounds = bird.y >= 0 and bird.y <= self.height
        within_bottom_pipe_y_bounds = bird.y + int(SCREEN_HEIGHT * BIRD_HEIGHT_PERCENT_TO_SCREEN) >= self.height + int(3 * BIRD_HEIGHT_PERCENT_TO_SCREEN * SCREEN_HEIGHT) and bird.y <= SCREEN_HEIGHT
        return within_pipe_x_bounds and (within_top_pipe_y_bounds or within_bottom_pipe_y_bounds)

# Game Manager class
class GameManager:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.is_game_over = False

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.is_game_over = False

    def update(self):
        if not self.is_game_over:
            self.bird.update()
            print("y coor: ", self.bird.y)

            if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH // 2:
                self.pipes.append(Pipe())

            for pipe in self.pipes:
                pipe.update()
                if pipe.is_offscreen():
                    self.pipes.remove(pipe)
                    self.score += 1
                if pipe.collide(self.bird):
                    self.is_game_over = True

    def draw(self, screen):
        self.bird.draw(screen)
        for pipe in self.pipes:
            pipe.draw(screen)
        screen.blit(base_image, (0, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.1)))

        # Draw score
        font = pygame.font.Font(None, 74)
        text = font.render(str(self.score), 1, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2, 50))

# Game loop
game = GameManager()
clock = pygame.time.Clock()

running = True
last_update = time.time()

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()
    if current_time - last_update >= 0.1:  # Polling rate of 0.1 seconds
        game.update()
        last_update = current_time

    game.draw(screen)

    pygame.display.flip()
    clock.tick(30)  # 30 FPS

    if game.is_game_over:
        print("Game Over! Final Score:", game.score)
        pygame.time.wait(2000)  # Wait for 2 seconds
        game.reset()

pygame.quit()