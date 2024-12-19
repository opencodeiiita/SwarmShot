#Code for the pet Class
import pygame

class Pet:
    def __init__(self, x, y, player):
        """Initialize a pet following the player."""
        self.x = x
        self.y = y
        self.player = player  # Reference to the player

    def update(self):
        """Make the pet follow the player (placeholder)."""
        self.x = self.player.x - 40  # Example offset
        self.y = self.player.y + 40

    def draw(self, surface):
        """Draw the pet on the screen (placeholder)."""
        pygame.draw.circle(surface, (255, 182, 193), (self.x, self.y), 10)
