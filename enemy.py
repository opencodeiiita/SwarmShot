#Code for Enemy
import pygame

class Enemy:
    def __init__(self, x, y):
        """Initialize the base Enemy."""
        self.x = x
        self.y = y
        self.health = 10  # Default enemy health

    def update(self):
        """Update enemy position and state (placeholder)."""
        pass

    def draw(self, surface):
        """Draw the enemy on the screen (placeholder)."""
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y, 32, 32))
