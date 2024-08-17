import pygame
import random
import cv2
import numpy as np

# Initialize Pygame
pygame.init()

# Initialize face classifier
face_classifier = cv2.CascadeClassifier("src/haarcascade_frontalface_default.xml")
video_cam = cv2.VideoCapture(0)

if not video_cam.isOpened():
    print("Cannot access the camera")
    exit()

# Get camera resolution
SCREEN_WIDTH = int(video_cam.get(cv2.CAP_PROP_FRAME_WIDTH))
SCREEN_HEIGHT = int(video_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set up the display with camera resolution
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Pygame")

# Constants
PIPE_WIDTH = 50
PIPE_SPEED = 15
BIRD_HEIGHT_PERCENT_TO_SCREEN = 0.05
BIRD_X_POS = SCREEN_WIDTH // 4

# Colors
WHITE = (255, 255, 255)

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
        self.y = SCREEN_HEIGHT // 2

    def update(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            # Find the face with the maximum area
            max_area_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = max_area_face
            self.y = y + h // 2  # Update bird's y position based on the largest face detected

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
        screen.blit(pipe_image, (self.x, self.height + int(3.5 * BIRD_HEIGHT_PERCENT_TO_SCREEN * SCREEN_HEIGHT)))

    def is_offscreen(self):
        return self.x < -PIPE_WIDTH

    def collide(self, bird):
        within_pipe_x_bounds = bird.x +50 > self.x and bird.x < self.x + PIPE_WIDTH
        
        within_top_pipe_y_bounds = bird.y-25 >= 0 and bird.y < self.height
        
        within_bottom_pipe_y_bounds = bird.y-25 + int(SCREEN_HEIGHT * BIRD_HEIGHT_PERCENT_TO_SCREEN) > self.height + int(3.5 * BIRD_HEIGHT_PERCENT_TO_SCREEN * SCREEN_HEIGHT) and bird.y <= SCREEN_HEIGHT
        
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

    def update(self, frame):
        if not self.is_game_over:
            self.bird.update(frame)

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
while running:
    ret, frame = video_cam.read()
    if ret:
        # Rotate the frame 90 degrees clockwise if needed
        frame_render = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Use the original frame directly without resizing
        frame_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame_render, cv2.COLOR_BGR2RGB))
        screen.blit(frame_surface, (0, 0))  # Draw the webcam feed as background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update(frame)  # Update game state with the current frame
        game.draw(screen)  # Draw the game elements

        pygame.display.flip()  # Update the display
        clock.tick(30)  # Maintain 30 FPS

        if game.is_game_over:
            print("Game Over! Final Score:", game.score)
            pygame.time.wait(2000)  # Wait for 2 seconds before resetting
            game.reset()

video_cam.release()
cv2.destroyAllWindows()
pygame.quit()