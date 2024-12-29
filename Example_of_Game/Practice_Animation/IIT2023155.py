import pygame
import sys
# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
SHADOW_COLOR = (50, 50, 50, 100)
PINK=(255,182,193)
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
        self.sprite_sheet = pygame.image.load("Sprites\Sprites_Pet\PET_Cat_Gray.png").convert_alpha()

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 8  # Adjust this for animation speed

        # Directions and frames
        self.direction = "down"  # Starting direction
        self.current_action= "down_idle"
        self.frames = self.load_frames()

        # Movement state
        self.moving = False
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.background_color = WHITE  # Default background color
        self.color_mapping = {  
            "up": PINK,    # Pink
            "down": (173, 216, 230),  # Light Blue
            "left": (177, 156, 217),  # Light Purple
            "right": (144, 238, 144)  # Light Green
        }
    def load_frames(self):
        """Extract movement frames from the spritesheet."""
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
        self.moving = False  # Reset moving state

        # Movement logic
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
            self.current_action = "up_move"
            self.background_color=self.color_mapping["up"]
        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
            self.current_action = "down_move"
            self.background_color=self.color_mapping["down"]
        elif keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
            self.current_action = "left_move"
            self.background_color=self.color_mapping["left"]
        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
            self.current_action = "right_move"
            self.background_color=self.color_mapping["right"]
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
        if not self.moving:
            self.pulse_scale += 0.003 * self.pulse_direction
            if self.pulse_scale > 1.02 or self.pulse_scale < 0.96:
                self.pulse_direction *= -1
    def draw(self, surface):
        shadow = pygame.Surface((128, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, SHADOW_COLOR, (0, 0, 128, 32))
        surface.blit(shadow, (self.x, self.y + 96))

        scaled_image = pygame.transform.scale(
            self.frames[self.current_action][self.current_frame],
            (int(128 * self.pulse_scale), int(128 * self.pulse_scale)),
        )
        surface.blit(scaled_image, (self.x, self.y))
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
        screen.fill(player.background_color)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main()
