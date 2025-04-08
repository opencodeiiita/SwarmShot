import pygame
import sys
import random
from player import Player
from enemy import FlyingEye, Goblin, Mushroom, Skeleton, EvilWizard, BigFlyingEye, DashingGoblin,EnemySwarm, TeleportingMushroom
from weapon import WeaponManager

# Initialize Pygame
pygame.init()

# Screen Dimensions
TILE_SIZE = 16
GRID_SIZE = 44
MAP_WIDTH = TILE_SIZE * GRID_SIZE
MAP_HEIGHT = TILE_SIZE * GRID_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load tile and map resources
DESERT_TILE = pygame.image.load("Sprites/Sprites_Environment/desert_tile.png")  # Use forward slashes
DESERT_TILE = pygame.transform.scale(DESERT_TILE, (TILE_SIZE, TILE_SIZE))  # Resize tile to 16x16

# Set up display
screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
pygame.display.set_caption("SwarmShot by IIITA")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load Player
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

weapon_manager = WeaponManager()

# Define Enemy Wave Data
waves = [
    # Introduction waves
    {
        'enemies': [(FlyingEye, 8, 1.5),(DashingGoblin, 6, 2)],
        'message': "Wave 1: Scout Flying Eyes Approaching!"
    },
    {
        'enemies': [(BigFlyingEye, 2, 1.5),(Goblin, 4, 2)],
        'message': "Wave 2: Mini-Boss!"
    },
    {
        'enemies': [(FlyingEye, 8, 1.5), (Goblin, 5, 2), (TeleportingMushroom, 3, 1)],
        'message': "Wave 3: Combined Forces!"
    },

    # Mid-game challenge
    {
        'enemies': [(Skeleton, 10, 1.5), (FlyingEye, 15, 1), (TeleportingMushroom, 4, 1)],
        'message': "Wave 4: Skeletons Join the Fray!"
    },
    {
        'enemies': [(Mushroom, 5, 2), (Goblin, 12, 1), (FlyingEye, 10, 1.2), (TeleportingMushroom, 6, 1)],
        'message': "Wave 5: Unrelenting Onslaught!"
    },

    # Final wave
    {
        'enemies': [(EvilWizard, 2, 3), (Mushroom, 10, 1), (Goblin, 10, 1.5), (Skeleton, 20, 0.8), (TeleportingMushroom, 8, 1)],
        'message': "Wave 6: FINAL WAVE: Ultimate Challenge!"
    }
]


class WaveManager:
    def __init__(self):
        self.wave_index = 0
        self.enemies = []
        self.spawn_timer = 0
        self.wave_message = ""
        self.message_timer = 0
        self.time_between_waves = 5  # Time in seconds between waves
        self.wave_completed = False
        self.wave_cooldown = 0
        self.squads = []  # Added for squad management
        self.obstacle_map = [[False for _ in range(GRID_SIZE)]
                           for _ in range(GRID_SIZE)]  # For pathfinding
    def _generate_obstacle_map(self):
        """Generates an obstacle map for enemy pathfinding (placeholder implementation)."""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                # Example: Mark edges as obstacles (modify as needed)
                if x == 0 or y == 0 or x == GRID_SIZE - 1 or y == GRID_SIZE - 1:
                    self.obstacle_map[y][x] = True
    def _generate_patrol_path(self, enemy):
        """Generates a simple patrol path for an enemy."""
        path = []
        for _ in range(5):  # Create a 5-point patrol path
            x = random.randint(0, GRID_SIZE - 1) * TILE_SIZE
            y = random.randint(0, GRID_SIZE - 1) * TILE_SIZE
            path.append((x, y))
        return path


    def start_wave(self):
        if self.wave_index >= len(waves):
            return False  # No more waves

        wave_data = waves[self.wave_index]
        self.enemies = []
        self.wave_message = wave_data['message']
        self.message_timer = pygame.time.get_ticks()
        self.wave_completed = False

        # Spawn enemies
        for enemy_type, count, spawn_rate in wave_data['enemies']:
            for _ in range(count):
                x = random.randint(0, GRID_SIZE - 1) * TILE_SIZE
                y = random.randint(0, GRID_SIZE - 1) * TILE_SIZE
                enemy = enemy_type(x, y)
                self.enemies.append(enemy)
                enemy.spawn_rate = spawn_rate

        # Initialize obstacle map
        self._generate_obstacle_map()

        # Initialize squads
        self._organize_into_squads(wave_data)

        # Initialize AI systems for each enemy
        for enemy in self.enemies:
            enemy.obstacle_map = self.obstacle_map
            enemy.patrol_path = self._generate_patrol_path(enemy)

        return True

    def _organize_into_squads(self, wave_data):
        """Organize enemies into coordinated squads"""
        self.squads = []
        squad_size = 4  # Enemies per squad

        for i in range(0, len(self.enemies), squad_size):
            squad = EnemySwarm(self.enemies[i:i+squad_size])
            squad.strategy = random.choice(["flank", "swarm", "cover"])
            self.squads.append(squad)

    def update(self):
        for enemy in self.enemies:
            if enemy.spawn_rate and not enemy.is_dead:
                enemy.update(player)  # Changed from regular update

                # Line of sight check
                if enemy.has_line_of_sight(player):
                    enemy.last_seen_player_pos = (player.x, player.y)

                # Environmental awareness
                if random.random() < 0.02:  # 2% chance per frame to replan path
                    enemy.current_path = enemy.pathfind_to_player(player)

        # Clean up dead enemies that have completed their death animation
        self.enemies = [enemy for enemy in self.enemies
                        if not (enemy.is_dead and enemy.death_animation_completed)]

        # Check if wave is complete
        if len(self.enemies) == 0 and not self.wave_completed:
            self.wave_completed = True
            self.wave_cooldown = pygame.time.get_ticks()

        # Start next wave after cooldown
        if self.wave_completed:
            if pygame.time.get_ticks() - self.wave_cooldown > self.time_between_waves * 1000:
                self.wave_index += 1
                if not self.start_wave():  # Returns False if no more waves
                    print("Game Completed!")
                    return

        # Handle enemy spawning
        for enemy in self.enemies:
            if enemy.spawn_rate:
                enemy.update(player)

    def draw(self, surface):
        if DEBUG_MODE:
            for enemy in self.enemies:
                enemy.draw_path(surface)
        # Draw all enemies
        for enemy in self.enemies:
            enemy.draw(surface)
# Add debug mode toggle
DEBUG_MODE = False

# Initialize Wave Manager
wave_manager = WaveManager()

# Function to render a basic map
def render_map():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            screen.blit(DESERT_TILE, (x * TILE_SIZE, y * TILE_SIZE))

# Function to draw the health bar
def draw_health_bar(surface, x, y, health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (health / max_health) * bar_width
    border_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, RED, border_rect, 2)

# Main game loop
def main():
    wave_manager.start_wave()  # Start the first wave
    player_health = player.health
    max_health = 100

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle player movement
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update wave manager
        wave_manager.update()

        # Check for health reduction here (after collision)
        player_health = player.health  # Update player health after enemies hit

        # Render everything
        screen.fill(WHITE)  # Optional fallback color
        render_map()
        # Update weapons
        weapon_manager.update(player.x, player.y, wave_manager.enemies)
        player.draw(screen)
        # Draw weapons
        weapon_manager.draw(screen)
        wave_manager.draw(screen)  # Draw the enemies

        # Display wave message
        if pygame.time.get_ticks() - wave_manager.message_timer < 2000:
            font = pygame.font.Font(None, 36)
            text = font.render(wave_manager.wave_message, True, WHITE)
            screen.blit(text, (MAP_WIDTH // 2 - text.get_width() // 2, MAP_HEIGHT // 2 - text.get_height() // 2))

        # Draw health bardd
        draw_health_bar(screen, 10, 10, player_health, max_health)

        # Check player health and display game over if health is 0
        if player_health <= 0:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (MAP_WIDTH // 2 - game_over_text.get_width() // 2, MAP_HEIGHT // 2 - game_over_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    main()
