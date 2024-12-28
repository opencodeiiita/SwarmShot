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

        #Pet folder is set here 
        folder = "Sprites/Sprites_Pet/"

        #Different pet can be changed here by just writing there name
        character = "PET_Fox.png"
        
        # Load spritesheets
        self.sprite_sheet = pygame.image.load(f"{folder}{character}").convert_alpha()
        self.idle_sprite_sheet = pygame.image.load(f"{folder}{character}").convert_alpha()


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
        
        #directions were changes to adjust frames of the image
        directions = ["down", "left", "right", "up"]  # Order in the spritesheet

        start_row = 5 # I count the rows as 0, 1 , 2 ....

        print("Frames: ")
        for direction_index, direction in enumerate(directions):
            for row_offset in range(2):  # Each direction uses 2 rows
                for col in range(4):  # Each row has 4 columns
                    x = (col * frame_size)
                    y = ((direction_index * 2 + row_offset) * frame_size) + (start_row * frame_size) #Just had to add the y offset
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

        print("Idle Frames: ")
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

        #Changed the conditions here, basically bring out the inner condition( timer> frame_delay) as the super condition
        #and then checking for self.moving

        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if self.moving:
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            else:
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames[self.direction])


    def draw(self, surface):
        """Draw the player on the screen."""
        if self.moving:
                current_frames = self.frames[self.direction]
        else:
            current_frames = self.idle_frames[self.direction]

        frame_index = self.current_frame % len(current_frames)

        enlarge = pygame.transform.scale(current_frames[frame_index], (64,64))
        surface.blit(enlarge, (self.x, self.y))

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