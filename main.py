import pygame
import sys
from player import Player
from enemy import Enemy
from pet import Pet
from weapon import Weapon
from building import Building
from shop import Shop

# Initialize Pygame
pygame.init()

# Screen Dimensions
TILE_SIZE = 16
GRID_SIZE = 44
MAP_WIDTH = TILE_SIZE * GRID_SIZE
MAP_HEIGHT = TILE_SIZE * GRID_SIZE

# Colors (optional background fallback)
WHITE = (255, 255, 255)

# Load tile and map resources
DESERT_TILE = pygame.image.load('Sprites/Sprites_Environment/desert_tile.png')  # Replace 'desert_tile.png' with your desert tile image
DESERT_TILE = pygame.transform.scale(DESERT_TILE, (TILE_SIZE, TILE_SIZE))  # Resize tile to 16x16

# Set up display
screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
pygame.display.set_caption("SwarmShot by IIITA")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load Player
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
# Placing player at centre of map

# Function to render a basic map
def render_map():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            screen.blit(DESERT_TILE, (x * TILE_SIZE, y * TILE_SIZE))

# Main game loopS
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle player movement
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Render everything
        screen.fill(WHITE)  # Optional fallback color
        render_map()
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    main()
