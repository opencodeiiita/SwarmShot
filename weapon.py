#code for weapon
import pygame

class Weapon:
    def __init__(self, bullet_speed=5):
        """Initialize a weapon."""
        self.bullet_speed = bullet_speed
        self.bullets = []

    def shoot(self, x, y):
        """Add a bullet at a given position."""
        bullet = {"x": x, "y": y, "speed": self.bullet_speed}
        self.bullets.append(bullet)

    def update(self):
        """Update bullet positions."""
        for bullet in self.bullets:
            bullet["y"] -= bullet["speed"]  # Move bullet upward

    def draw(self, surface):
        """Draw bullets."""
        for bullet in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), (bullet["x"], bullet["y"], 5, 10))
