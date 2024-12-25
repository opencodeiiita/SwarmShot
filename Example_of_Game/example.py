import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen Dimensions
TILE_SIZE = 16
GRID_SIZE = 30
MAP_WIDTH = TILE_SIZE * GRID_SIZE
MAP_HEIGHT = TILE_SIZE * GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BROWN = (181, 101, 29)
DARK_BROWN = (101, 67, 33)

# Pygame Screen Setup
screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
pygame.display.set_caption("Zombie Horde Survivor")
clock = pygame.time.Clock()

# Game Settings
PLAYER_SPEED = 5
BULLET_SPEED = 10
BULLET_DAMAGE = 2
PLAYER_HEALTH = 30
ENEMY_HEALTH = 4
ENEMY_SPEED = 2

# --- Utility Functions ---
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load("Sprites/Sprites_Pet/PET_Fox.png").convert_alpha()

        # Animation settings
        self.frame_width = 72   # Update to match your sprite sheet's frame width
        self.frame_height = 72  # Update to match your sprite sheet's frame height
        self.frames_per_row = 4  # Update to match your sprite sheet layout
        self.current_frame = 0
        self.animation_speed = 10  # Adjust for animation speed
        self.frame_timer = 0

        # Extract animation frames
        self.frames = self.load_frames()

        # Initial player state
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.moving = False

    def load_frames(self):
        """Extract frames from the sprite sheet."""
        frames = []
        for row in range(self.frames_per_row):
            for col in range(self.frames_per_row):
                x = col * self.frame_width
                y = row * self.frame_height
                frame = self.sprite_sheet.subsurface((x, y, self.frame_width, self.frame_height))
                frames.append(frame)
        return frames

    def update(self, keys_pressed):
        dx, dy = 0, 0
        self.moving = False  # Reset moving state

        # Movement logic
        if keys_pressed[pygame.K_w]: 
            dy -= self.speed
            self.moving = True
        if keys_pressed[pygame.K_s]: 
            dy += self.speed
            self.moving = True
        if keys_pressed[pygame.K_a]: 
            dx -= self.speed
            self.moving = True
        if keys_pressed[pygame.K_d]: 
            dx += self.speed
            self.moving = True

        # Update position with bounds
        self.rect.x = max(0, min(MAP_WIDTH - self.rect.width, self.rect.x + dx))
        self.rect.y = max(0, min(MAP_HEIGHT - self.rect.height, self.rect.y + dy))

        # Animation logic
        self.frame_timer += 1
        if self.moving:
            if self.frame_timer >= self.animation_speed:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        if not self.moving:
            self.image = self.frames[0]  # Set to a dedicated idle frame if available.


# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED

    def update(self, player):
        if self.health <= 0:
            self.kill()
            return

        # Move toward the player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        self.rect.x += self.speed * dx / dist
        self.rect.y += self.speed * dy / dist


# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.speed = BULLET_SPEED
        self.direction = self.calculate_direction()

    def calculate_direction(self):
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        return dx / dist, dy / dist

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if not screen.get_rect().colliderect(self.rect):
            self.kill()


# --- Weapon Class ---
class Weapon:
    def __init__(self, owner):
        self.owner = owner  # The player
        self.reload_timer = 0
        self.reload_rate = 30  # Fire every 30 frames

    def shoot(self, bullets, enemies):
        if self.reload_timer > 0:
            self.reload_timer -= 1
            return

        # Find the nearest enemy
        if enemies:
            nearest_enemy = min(enemies, key=lambda e: distance(self.owner.rect.center, e.rect.center))
            if nearest_enemy:
                bullet = Bullet(self.owner.rect.centerx, self.owner.rect.centery, nearest_enemy)
                bullets.add(bullet)
                self.reload_timer = self.reload_rate


# --- Game Setup ---
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
player_group = pygame.sprite.GroupSingle(player)

enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Add an initial weapon
weapon = Weapon(player)
player.weapons.append(weapon)

# --- Wave System ---
wave = 1
def spawn_enemies(num):
    for _ in range(num):
        x, y = random.choice([(random.randint(0, MAP_WIDTH), random.choice([0, MAP_HEIGHT])),
                              (random.choice([0, MAP_WIDTH]), random.randint(0, MAP_HEIGHT))])
        enemy = Enemy(x, y)
        enemies.add(enemy)


spawn_enemies(5)  # Initial wave


# --- Main Game Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill(DARK_BROWN)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Game Logic ---
    keys_pressed = pygame.key.get_pressed()
    player_group.update(keys_pressed)
    enemies.update(player)
    bullets.update()

    # Auto-aim Weapons
    for weapon in player.weapons:
        weapon.shoot(bullets, enemies)

    # Bullet-Enemy Collision
    for bullet in bullets:
        hit = pygame.sprite.spritecollideany(bullet, enemies)
        if hit:
            hit.health -= BULLET_DAMAGE
            bullet.kill()

    # Player-Enemy Collision (damage player)
    if pygame.sprite.spritecollideany(player, enemies):
        player.health -= 0.1  # Continuous damage on collision
        if player.health <= 0:
            print("Game Over!")
            pygame.quit()
            sys.exit()

    # Wave Clear Check
    if not enemies:
        wave += 1
        print(f"Wave {wave}!")
        spawn_enemies(wave * 5)  # Increase enemy count per wave

    # --- Drawing ---
    # Draw Tiles
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    player_group.draw(screen)
    enemies.draw(screen)
    bullets.draw(screen)

    # Health Bar
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player.health / PLAYER_HEALTH), 20))

    # Display Wave
    font = pygame.font.SysFont(None, 36)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(wave_text, (MAP_WIDTH - 150, 10))

    # --- Update Display ---
    pygame.display.flip()
