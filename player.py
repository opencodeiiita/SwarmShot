#Code for Main player

import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4  # Movement speed

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Player/mega_scientist_walk.png").convert_alpha()
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjusts animation speed

        # Player direction and frame setup
        self.direction = "down"  # Default direction
        self.frames = self.load_frames()

    def load_frames(self):
        """Extract frames from sprite sheet for animation."""
        frames = {
            #Explaintation: (x,y,Width,Height)
            #Top-left of sprite-sheet is 0,0 cordinate
            #In properties , you see mega_scientist_walk is 576*256 pixels
            #64X64 is each grid
            "up": [self.sprite_sheet.subsurface((i * 64, 0, 64, 64)) for i in range(8)],
            "left": [self.sprite_sheet.subsurface((i * 64, 64, 64, 64)) for i in range(8)],
            "down": [self.sprite_sheet.subsurface((i * 64, 128, 64, 64)) for i in range(8)],
            "right": [self.sprite_sheet.subsurface((i * 64, 192, 64, 64)) for i in range(8)],
        }
        return frames

    def update(self, keys):
        """Update player position and animation based on input."""
        moving = False

        # Movement logic
        #up-down 
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            self.direction = "down"
            moving = True
        #left-right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
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
            self.current_frame = 0  # Idle state resets to the first frame

    def draw(self, surface):
        """Draw the player sprite on the screen."""
        surface.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))
