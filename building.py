#Code for the Building
import pygame

class Building:
    def __init__(self, x, y):
        """Initialize a basic building."""
        self.x = x
        self.y = y

    def update(self):
        """Update building state (placeholder)."""
        pass

    def draw(self, surface):
        """Draw the building (placeholder)."""
        pygame.draw.rect(surface, (139, 69, 19), (self.x, self.y, 64, 64))
