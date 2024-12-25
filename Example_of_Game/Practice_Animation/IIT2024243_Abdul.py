import pygame
import sys, cv2

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
        character = "PET_Racoon.png"
        char = character[:-4]
        
        #As the whole image has idle and moving frames, I had split the image into two other images just like the char03.png
        image = cv2.imread(f"{folder}{character}", cv2.IMREAD_UNCHANGED)

        #cropping for the images is done here
        frame, rows_to_crop = 32, 4
        idle_img = image[0:rows_to_crop*frame, 0:image.shape[1]]
        moving_img = image[(rows_to_crop+1)*frame:, :]  # Removed +1 from cropping

        #images are saved in the same directory of Pet's
        cv2.imwrite(f"{folder}{char}_Idle.png", idle_img)
        cv2.imwrite(f"{folder}{char}_Movement.png", moving_img)

        # Load spritesheets
        self.sprite_sheet = pygame.image.load(f"{folder}{char}_Movement.png").convert_alpha()
        self.idle_sprite_sheet = pygame.image.load(f"{folder}{char}_Idle.png").convert_alpha()


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
        directions = ["down", "left", "right", "up"]  # Order in the spritesheet

        for direction_index, direction in enumerate(directions):
            for row_offset in range(2):  # Each direction uses 2 rows
                for col in range(4):  # Each row has 4 columns
                    x = col * frame_size
                    y = (direction_index * 2 + row_offset) * frame_size
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
        surface.blit(current_frames[frame_index], (self.x, self.y))

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
