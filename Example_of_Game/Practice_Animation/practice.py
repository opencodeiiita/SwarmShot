# This is the file for basic issues and practice tasks.
# Please use **VS Code** (other editors are fine too if you prefer).
#
# **Issue 2**: Animate the character "Char_003.png" on a screen display of size 800x600 using a spritesheet.
# 
# **Learning Resources**:
# - Refer to the `player.py` file for understanding how the character is animated.
# - Familiarize yourself with the concept of spritesheets and slicing frames using coordinates.
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

        # Load the spritesheet
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Player/Char_003.png").convert_alpha()
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust this for animation speed

        # Directions and frames
        self.direction = "down" #starting direction
        self.frames = self.load_frames()

    def load_frames(self):
        """Extract frames from spritesheet."""
        frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        frame_size = 72  # Size of each sprite frame
        directions = ["down", "left", "right", "up"]  # Order in the spritesheet

        for row, direction in enumerate(directions):
            for col in range(4):  # 4 frames per direction
                x, y = col * frame_size, row * frame_size
                frames[direction].append(self.sprite_sheet.subsurface((x, y, frame_size, frame_size)))

        return frames

    def update(self, keys):
        """Update player position and animation based on input."""
        moving = False

        # Movement logic
        if keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = "down"
            moving = True
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
            moving = True

        # Update animation frame
        if moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
        else:
            self.current_frame = 0  # Reset to the first frame when idle

    def draw(self, surface):
        """Draw the player on the screen."""
        surface.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))

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
