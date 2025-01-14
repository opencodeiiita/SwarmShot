import pygame

class Enemy:
    def __init__(self, x, y, speed, health, damage, scale=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.damage = damage  # Damage per second
        self.scale = scale
        self.frames = {}  # Dictionary to hold frames for different actions
        self.current_action = 'idle'
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust for animation speed

    def load_frame_sheet(self, sprite_file_path, frame_width, frame_height, rows, cols):
        """Loads a sprite sheet and returns a list of frames."""
        sprite_sheet = pygame.image.load(sprite_file_path).convert_alpha()
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = sprite_sheet.subsurface(
                    (col * frame_width, row * frame_height, frame_width, frame_height)
                )
                scaled_frame = pygame.transform.scale(
                    frame, (int(frame_width * self.scale), int(frame_height * self.scale))
                )
                frames.append(scaled_frame)
        return frames

    def update(self, player):
        """Update the enemy state, position, and check for collisions."""
        # Calculate the player's center
        player_center = (player.x, player.y)  

        # Calculate the enemy's center
        current_frame = self.frames[self.current_action][self.current_frame]
        enemy_center = (self.x ,self.y)

        # Calculate direction towards the player's center
        dx, dy = player_center[0] - enemy_center[0], player_center[1] - enemy_center[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance != 0:
            dx /= distance
            dy /= distance

        # Move enemy towards player's center
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_action])

        # Check collision with player
        enemy_rect = pygame.Rect(self.x, self.y, 50, 50)
        player_rect = pygame.Rect(player.x, player.y, 64, 64)
        if enemy_rect.colliderect(player_rect):
            player.health -= self.damage / 60  # Adjusting for per second damage


    def draw(self, surface):
        """Draw the current frame of the enemy on the screen."""
        sprite = self.frames[self.current_action][self.current_frame]
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
    
        # Draw the sprite
        surface.blit(sprite, sprite_rect.topleft)

        # Draw a pink rectangle for visualization  ##dont delete these 2 lines
        #pygame.draw.rect(surface, (255, 0, 255), sprite_rect, 2)  # Pink color, 2-pixel border



# Specific enemy classes with their own load_frames functions
class EvilWizard(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, health=300, damage=5, scale=1.5)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Evil Wizard."""
        self.frames['attack1'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Attack1.png", 250, 250, 1, 8)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Attack2.png", 250, 250, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Death.png", 250, 250, 1, 7)
        self.frames['chau'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Idle.png", 250, 250, 1, 8)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Run.png", 250, 250, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Take hit.png", 250, 250, 1, 3)

class FlyingEye(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=50, damage=1, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Flying Eye."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Take Hit.png", 150, 150, 1, 4)

# Similar classes for Goblin, Mushroom, and Skeleton
class Goblin(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, health=75, damage=3, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Goblin."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Idle.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Run.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Take Hit.png", 150, 150, 1, 4)

class Mushroom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=2, health=200, damage=5, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Mushroom."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Idle.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Run.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Take Hit.png", 150, 150, 1, 4)

class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=3, health=100, damage=20, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Skeleton."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Idle.png", 150, 150, 1, 4)
        self.frames['shield'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Shield.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Walk.png", 150, 150, 1, 4)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Take Hit.png", 150, 150, 1, 4)
