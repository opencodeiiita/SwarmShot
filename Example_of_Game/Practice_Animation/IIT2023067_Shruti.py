import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRAIL_COLOR = (150, 150, 150)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sprite Animation Practice - Enhanced")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Trail class
class Trail:
    def __init__(self, x, y, size, lifetime):
        self.x = x
        self.y = y
        self.size = size
        self.lifetime = lifetime

    def draw(self, surface):
        alpha = max(0, int(255 * (self.lifetime / 30)))  # Fade effect
        trail_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(trail_surf, TRAIL_COLOR + (alpha,), (self.size // 2, self.size // 2), self.size // 2)
        surface.blit(trail_surf, (self.x, self.y))

    def update(self):
        self.lifetime -= 1

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4  # Movement speed
        self.boosted_speed = 8  # Speed when boosted

        # Load the main spritesheet
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_Racoon.png").convert_alpha()

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust this for animation speed

        # Directions and frames
        self.direction = "down"  # Starting direction
        self.current_action = "down_idle"
        self.frames = self.load_frames()
        self.trails = []

    def load_frames(self):
        """Extract frames from the sprite sheet for animation."""
        frames = {
            # Format: [self.sprite_sheet.subsurface((x, y, width, height))]
            "up_idle": [self.sprite_sheet.subsurface((i * 32, 96, 32, 32)) for i in range(4)],
            "up_move": [self.sprite_sheet.subsurface((i * 32, 352, 32, 32)) for i in range(4)],
            "down_idle": [self.sprite_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(4)],
            "down_move": [self.sprite_sheet.subsurface((i * 32, 160, 32, 32)) for i in range(4)],
            "left_idle": [self.sprite_sheet.subsurface((i * 32, 64, 32, 32)) for i in range(4)],
            "left_move": [self.sprite_sheet.subsurface((i * 32, 224, 32, 32)) for i in range(4)],
            "right_idle": [self.sprite_sheet.subsurface((i * 32, 32, 32, 32)) for i in range(4)],
            "right_move": [self.sprite_sheet.subsurface((i * 32, 288, 32, 32)) for i in range(4)],
        }
        return frames

    def update(self, keys):
        """Update player position and animation based on input."""
        moving = False
        speed = self.boosted_speed if keys[pygame.K_SPACE] else self.speed  # Boost logic

        # Movement logic
        if keys[pygame.K_UP]:
            self.y -= speed
            self.current_action = "up_move"
            moving = True
        elif keys[pygame.K_DOWN]:
            self.y += speed
            self.current_action = "down_move"
            moving = True
        elif keys[pygame.K_LEFT]:
            self.x -= speed
            self.current_action = "left_move"
            moving = True
        elif keys[pygame.K_RIGHT]:
            self.x += speed
            self.current_action = "right_move"
            moving = True
        else:
            # Default idle state with bounce
            if "up" in self.current_action:
                self.current_action = "up_idle"
            elif "down" in self.current_action:
                self.current_action = "down_idle"
            elif "left" in self.current_action:
                self.current_action = "left_idle"
            elif "right" in self.current_action:
                self.current_action = "right_idle"
            self.y += random.choice([-1, 1])  # Bounce effect

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_action])

        # Add trail effect
        if moving:
            self.trails.append(Trail(self.x + 48, self.y + 48, 20, 30))

        # Update trails
        self.trails = [trail for trail in self.trails if trail.lifetime > 0]
        for trail in self.trails:
            trail.update()

    def apply_tint(self, image, tint_color):
        """Apply a color tint to the image."""
        tinted_image = image.copy()
        tint_surface = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(tint_color + (50,))  # Tint color with transparency
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return tinted_image

    def draw(self, surface):
        """Draw the player and trails on the screen."""
        # Draw trails
        for trail in self.trails:
            trail.draw(surface)

        # Apply tint to the current frame
        current_image = self.frames[self.current_action][self.current_frame]
        tinted_image = self.apply_tint(current_image, (random.randint(0, 50), 0, random.randint(0, 50)))

        # Scale and rotate for effect
        scaled_image = pygame.transform.scale(tinted_image, (128, 128))  # Scale to 4x size
        rotated_image = pygame.transform.rotate(scaled_image, random.randint(-5, 5))
        surface.blit(rotated_image, (self.x, self.y))

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
        screen.fill(BLACK)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main()
