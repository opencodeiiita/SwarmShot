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
        # Load the idle spritesheet
        self.idle_sprite_sheet = self.sprite_sheet

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
        """Extract movement frames from the spritesheet."""
        frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        frame_size = 32  # Size of each sprite frame
        #there are total 8 frames in two lines for each animation
        directions = ["down", "down", "left", "left", "right", "right", "up", "up"]  # Order in the spritesheet
        #the first 5 are related to idle animation
        offset = 5
        for row, direction in enumerate(directions):
            for col in range(4):  # 4 frames per direction
                x, y = col * frame_size, (row+offset) * frame_size
                frames[direction].append(self.sprite_sheet.subsurface((x, y, frame_size, frame_size)))

        return frames

    def load_idle_frames(self):
        """Extract idle frames from the idle spritesheet."""
        idle_frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        frame_size = 32  # Size of each sprite frame
        directions = ["down", "right", "left", "up"]  # Order in the spritesheet

        for row, direction in enumerate(directions):
            for col in range(4):  # 4 frames per direction
                x, y = col * frame_size, row * frame_size
                idle_frames[direction].append(self.idle_sprite_sheet.subsurface((x, y, frame_size, frame_size)))

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
        if self.moving:
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1)
            self.current_frame %= len(self.frames[self.direction])
        else:
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1)
            self.current_frame %= len(self.idle_frames[self.direction])
        
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
