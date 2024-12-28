# This is the file for Issue 2.
# Please use **VS Code** (other editors are fine too if you prefer).
#
# Given : An Animated character "Char_003.png" on a screen display of size 800x600 using a spritesheet.
# **Issue 2**: Replace this character with any of the favourite sprite sheet.
#
# **Note**:
# 1. While referring to any file, use the 'Copy Relative Path' option in VS Code.
#    The path should always be relative to the **main repository** (root directory: `SwarmShot` folder).
#    Example: `Sprites\Sprites_Player\Char_003.png`
# 2. In Python, `\m` and similar sequences are treated as escape characters.
#    Therefore, always replace `\` with `/` in file paths.
#    Corrected example: `Sprites/Sprites_Player/Char_003.png`

# **How to Run this?
# Open the SwarmShot folder in V S Code , open practice.py file from left Explorer Panel .
# Press Run Code button 

# **Animation Details for Char_003.png**:
# - The character spritesheet `Sprites/Sprites_Player/Char_003.png` contains 16 images arranged in a 4x4 grid.
# - The top-left corner of the image is at coordinates (0, 0), and the bottom-right is at (width, height).
# - The total size of the image is 288 x 288 pixels. Each character frame is 72 x 72 pixels (288/4 = 72).
#
# **Accessing Frames**:
# - Each frame corresponds to a single character pose in the grid.
# - To access any frame:
#   (x, y) = ((column - 1) * frame_width, (row - 1) * frame_height)
# - Frame Examples:
#   - Top-left frame (1st row, 1st column): (0, 0, 72, 72)
#   - Frame in the 1st row, 2nd column: (72, 0, 72, 72)
#   - Frame in the 4th row, 3rd column: ((4 - 1) * 72, (3 - 1) * 72, 72, 72) => (216, 144, 72, 72)

# **Implementation Steps**:
# 1. Use the `pygame.image.load()` function to load the spritesheet (`Char_003.png`) as a surface.
# 2. Use `pygame.Surface.subsurface()` or slicing logic to extract individual frames.
# 3. Update the frame index in a loop to create animation for movement.
# 4. Implement an idle animation by playing the first frame or looping a subset of frames when the character isn’t moving.

# **Next Steps**:
# Now, let’s animate the player character using the spritesheet "Sprites/Sprites_Player/Char_003.png".






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
pygame.display.set_caption("Sprite Animation")

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
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_BlueBird.png").convert_alpha()

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
            self.y += random.choice([0, 0])  # Bounce effect

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_action])

        # Add trail effect
        if moving:
            self.trails.append(Trail(self.x + 60, self.y + 60, 20, 30))

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
        scaled_image = pygame.transform.scale(tinted_image, (90, 90))  # Scale to 4x size
        rotated_image = pygame.transform.rotate(scaled_image, random.randint(0, 0))
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
        clock.tick(30)  

if __name__ == "__main__":
    main()