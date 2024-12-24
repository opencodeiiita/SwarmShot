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
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_Racoon.png").convert_alpha()
        # Load the idle spritesheet
        self.idle_sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_Racoon.png").convert_alpha()

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
        """Extract movement frames from the spritesheet dynamically."""
        frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }

        # Get spritesheet dimensions
        sprite_width, sprite_height = self.sprite_sheet.get_size()

        # 13 rows and 4 columns (you mentioned these)
        rows = 13
        columns = 4

        # Frame width and height
        frame_width = sprite_width // columns
        frame_height = sprite_height // rows

        # Directions (Dynamic Mapping)
        directions = ["down", "right", "left", "up"]

        # Row Mapping for walking frames
        for row in range(rows):
            for col in range(columns):
                x, y = col * frame_width, row * frame_height

                # Check bounds and skip if out of range
                if x + frame_width > sprite_width or y + frame_height > sprite_height:
                    continue

                # Extract frame
                frame = self.sprite_sheet.subsurface((x, y, frame_width, frame_height))

                # Assign walking frames based on row mapping
                if row == 0:
                    frames["down"].append(frame)  # Walking down
                elif row == 1:
                    frames["right"].append(frame)  # Walking right
                elif row == 2:
                    frames["left"].append(frame)  # Walking left
                elif row == 3:
                    frames["up"].append(frame)  # Walking up
                elif row == 5:
                    frames["down"].append(frame)  # Walking down (2nd row for down)
                elif row == 6:
                    frames["down"].append(frame)  # Walking down (3rd row for down)
                elif row == 7:
                    frames["left"].append(frame)  # Walking left (2nd row for left)
                elif row == 8:
                    frames["left"].append(frame)  # Walking left (3rd row for left)
                elif row == 9 or row == 10:
                    frames["right"].append(frame)  # Walking right (4th and 5th rows for right)
                elif row == 11 or row == 12:
                    frames["up"].append(frame)  # Walking up (6th and 7th rows for up)

        return frames



    def load_idle_frames(self):
        """Extract idle frames from the idle spritesheet dynamically."""
        idle_frames = {
            "down": [],
            "right": [],
            "left": [],
            "up": []
        }

        # Get spritesheet dimensions
        sprite_width, sprite_height = self.idle_sprite_sheet.get_size()

        # 13 rows and 4 columns (as mentioned)
        rows = 13
        columns = 4

        # Frame width and height
        frame_width = sprite_width // columns
        frame_height = sprite_height // rows

        # Row Mapping for Idle frames:
        for row in range(rows):
            for col in range(columns):
                x, y = col * frame_width, row * frame_height

                # Check bounds and skip if out of range
                if x + frame_width > sprite_width or y + frame_height > sprite_height:
                    continue

                # Extract frame
                frame = self.idle_sprite_sheet.subsurface((x, y, frame_width, frame_height))

                # Assign idle frames based on the row mapping
                if row == 0:  # Idle facing down (row 1)
                    idle_frames["down"].append(frame)
                elif row == 1:  # Idle facing right (row 2)
                    idle_frames["right"].append(frame)
                elif row == 2:  # Idle facing left (row 3)
                    idle_frames["left"].append(frame)
                elif row == 3:  # Idle facing up (row 4)
                    idle_frames["up"].append(frame)
                elif row == 4:  # Idle poses for all directions (row 5)
                    if col == 0:  # Idle down
                        idle_frames["down"].append(frame)
                    elif col == 1:  # Idle right
                        idle_frames["right"].append(frame)
                    elif col == 2:  # Idle left
                        idle_frames["left"].append(frame)

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
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
        else:
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
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
