import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sprite Animation Practice")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5  # Movement speed

        # Load the main spritesheet
        self.sprite_sheet = pygame.image.load("Sprites\Sprites_Pet\PET_Fox.png").convert_alpha()

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust this for animation speed

        # Directions and frames
        self.direction = "down"  # Starting direction
        self.current_action = "down_idle"
        self.frames = self.load_frames()

    def load_frames(self):
        """Extract frames from the sprite sheet for animation."""
        frames = {
            # Format: [self.sprite_sheet.subsurface((x, y, width, height))]
            "up_idle": [self.sprite_sheet.subsurface((i * 32, 96, 32, 32)) for i in range(4)],
            "up_move": [self.sprite_sheet.subsurface((i * 32, (j+11)*32, 32, 32)) for j in range(2) for i in range(4)],
            "down_idle": [self.sprite_sheet.subsurface((i * 32, j*4*32, 32, 32)) for j in range(2) for k in range(3) for i in range(4)],
            "down_move": [self.sprite_sheet.subsurface((i * 32, (j + 5)* 32 , 32, 32)) for j in range(2) for i in range(4)],
            "left_idle": [self.sprite_sheet.subsurface((i * 32, 64, 32, 32)) for i in range(4)],
            "left_move": [self.sprite_sheet.subsurface((i * 32, (j+7)*32, 32, 32)) for j in range(2) for i in range(4)],
            "right_idle": [self.sprite_sheet.subsurface((i * 32, 32, 32, 32)) for i in range(4)],
            "right_move": [self.sprite_sheet.subsurface((i * 32, (j+9)*32, 32, 32)) for j in range(2) for i in range(4)],
        }
        return frames

    def update(self, keys):
        """Update player position and animation based on input."""
        # Movement logic
        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.y -= self.speed
            self.x += self.speed
            self.current_action = "right_move"

        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.y -= self.speed
            self.x -= self.speed
            self.current_action = "left_move"

        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.y += self.speed
            self.x -= self.speed
            self.current_action = "left_move"

        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            self.y += self.speed
            self.x += self.speed
            self.current_action = "right_move"

        elif keys[pygame.K_UP]:
            self.y -= self.speed
            self.current_action = "up_move"

        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.current_action = "down_move"

        elif keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.current_action = "left_move"

        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.current_action = "right_move"

        else:
            # Default idle state
            if "up" in self.current_action:
                self.current_action = "up_idle"
            elif "down" in self.current_action:
                self.current_action = "down_idle"
            elif "left" in self.current_action:
                self.current_action = "left_idle"
            elif "right" in self.current_action:
                self.current_action = "right_idle"

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_action])

    def draw(self, surface):
        """Draw the player on the screen, scaled up."""
        if self.current_action in self.frames and self.frames[self.current_action]:
        # Ensure current_frame is within range
            self.current_frame %= len(self.frames[self.current_action])

        # Fetch and draw the scaled frame
            scaled_image = pygame.transform.scale(self.frames[self.current_action][self.current_frame], (128, 128))
            surface.blit(scaled_image, (self.x, self.y))
        else:
            print(f"Draw error: Invalid action '{self.current_action}' or empty frame list.")

# Main game loop
def main():
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get key presses
        keys = pygame.key.get_pressed()

        # Update player
        player.update(keys)

        # Render everything
        screen.fill(WHITE)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main()
