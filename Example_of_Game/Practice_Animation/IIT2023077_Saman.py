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
        self.speed = 4  # Movement speed

        # Load the main spritesheet
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_Fox.png").convert_alpha()

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust this for animation speed

        # Directions and frames
        self.direction = "down"  # Starting direction
        self.frames = self.load_frames()
        self.idle_frames = self.load_idle_frames()

        # Movement state
        self.moving = False

    def load_frames(self):
        """Extract and scale movement frames from the spritesheet."""
        frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        frame_width = 32  # Original frame width
        frame_height = 32  # Original frame height
        scaled_width = 64  # Scaled frame width
        scaled_height = 64  # Scaled frame height
        directions = ["down", "left", "right", "up"]  

        for i in range(4):
            frames["down"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 160, frame_width, frame_height)), (scaled_width, scaled_height)))
            frames["left"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 224, frame_width, frame_height)), (scaled_width, scaled_height)))
            frames["right"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 288, frame_width, frame_height)), (scaled_width, scaled_height)))
            frames["up"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 352, frame_width, frame_height)), (scaled_width, scaled_height)))

        return frames


    def load_idle_frames(self):
        """Extract and scale idle frames for each direction."""
        idle_frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        frame_width = 32  # Original frame width
        frame_height = 32  # Original frame height
        scaled_width = 64  # Scaled frame width
        scaled_height = 64  # Scaled frame height
        directions = ["down", "left", "right", "up"]  

        for i in range(4):
            idle_frames["down"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 0, frame_width, frame_height)), (scaled_width, scaled_height)))
            idle_frames["left"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 64, frame_width, frame_height)), (scaled_width, scaled_height)))
            idle_frames["right"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 32, frame_width, frame_height)), (scaled_width, scaled_height)))
            idle_frames["up"].append(pygame.transform.scale(self.sprite_sheet.subsurface((i * 32, 96, frame_width, frame_height)), (scaled_width, scaled_height)))

        return idle_frames


    def update(self, keys):
        """Update player position and animation based on input."""
        self.moving = False  # Reset moving state

        # Movement logic
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
            self.moving = True
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
            self.moving = True
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
            self.moving = True
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
            self.moving = True

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if self.moving:
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            else:
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames[self.direction])

    def draw(self, surface):
        """Draw the player on the screen."""
        if self.moving:
            # Draw moving animation
            surface.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))
        else:
            # Draw idle animation
            surface.blit(self.idle_frames[self.direction][self.current_frame], (self.x, self.y))


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
