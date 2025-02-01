import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, speed, health, damage, acceptance_radius, scale=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.damage = damage  # Damage per second
        self.acceptance_radius = acceptance_radius  # Stop moving when within this distance
        self.scale = scale
        self.frames = {}  # Dictionary to hold frames for different actions
        self.current_action = 'idle'
        self.previous_action = None  # Track previous action 
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust for animation speed
        self.look_right=True
        ##For death
        self.is_dead = False                     
        self.is_taking_hit = False               
        self.hit_animation_timer = 0             
        self.death_animation_completed = False   

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

    def take_damage(self, damage):                                                      
        if not self.is_dead:                                                             
            self.health -= damage                                                       
            if self.health <= 0:                                                        
                self.is_dead = True                                                     
                self.current_action = 'death'                                           
                self.current_frame = 0                                                  
            else:                                                                       
                self.is_taking_hit = True                                                
                self.current_action = 'takehit'                                            
                self.current_frame = 0                                                  
                self.hit_animation_timer = len(self.frames['takehit']) * self.frame_delay  # Adjust based on animation length       


    def update(self, player):
        """Update the enemy state, position, and check for collisions."""

        if self.is_dead:                                                       
            # Complete death animation                                       
            self.frame_timer += 1                                           
            if self.frame_timer >= self.frame_delay:                            
                self.frame_timer = 0                                         
                if self.current_frame < len(self.frames['death']) - 1:        
                    self.current_frame += 1                                
                else:                                                   
                    self.death_animation_completed = True                  
            return  # Don't do anything else if dead                        

        if self.is_taking_hit:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                if self.current_frame < len(self.frames['takehit']) - 1:
                    self.current_frame += 1
                else:
                    self.is_taking_hit = False
                    self.current_frame = 0
            return  # Skip other updates while taking hit                                  

        # Calculate the player's center and enemy's center
        player_center = (player.x, player.y)
        enemy_center = (self.x ,self.y)  

        self.update_behavior(player)  # Call behavior logic before movement  

        # Calculate direction towards the player's center
        dx, dy = player_center[0] - enemy_center[0], player_center[1] - enemy_center[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Reset frame index if action changes
        if self.current_action != self.previous_action:
            self.current_frame = 0  # Reset animation frame
            self.previous_action = self.current_action  # Update previous action

        
        if distance > self.acceptance_radius:  # Move only if outside acceptance radius
            dx /= distance
            dy /= distance
            # Move enemy towards player's center
            self.x += dx * self.speed
            self.y += dy * self.speed

            #Update direction only when moving
            if dx > 0:
                self.look_right = True
            elif dx < 0:
                self.look_right = False

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if self.current_action in self.frames and len(self.frames[self.current_action]) > 0:        
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.current_action])   

        # Check collision with player
        enemy_rect = pygame.Rect(self.x, self.y, 50, 50)
        player_rect = pygame.Rect(player.x, player.y, 64, 64)
        if enemy_rect.colliderect(player_rect):
            player.health -= self.damage / 60  # Adjusting for per second damage

    def update_behavior(self, player):                                      
        """Default enemy behavior (to be overridden by subclasses)."""      
        pass


    def draw(self, surface):
        """Draw the current frame of the enemy on the screen."""
        sprite = self.frames[self.current_action][self.current_frame]

        if(self.look_right==False):
            sprite = pygame.transform.flip(sprite, True, False)
        sprite_rect = sprite.get_rect(center=(self.x, self.y))
        
        # Draw the sprite
        surface.blit(sprite, sprite_rect.topleft)

        ##Draw a pink rectangle for visualization  ##dont delete these 2 lines
        #pygame.draw.rect(surface, (255, 0, 255), sprite_rect, 2)  # Pink color, 2-pixel border



# Basic enemy classes with their own load_frames functions
class EvilWizard(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=200, damage=5, acceptance_radius=10, scale=1.5)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Evil Wizard."""
        self.frames['attack1'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Attack1.png", 250, 250, 1, 8)
        self.frames['attack2'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Attack2.png", 250, 250, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Death.png", 250, 250, 1, 7)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Idle.png", 250, 250, 1, 8)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Run.png", 250, 250, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Evil Wizard/Take hit.png", 250, 250, 1, 3)
    
    def update_behavior(self, player):
        """Wizard Boss chase and attack when close."""
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        new_action = 'idle' if distance > 150 else 'attack2' if distance > self.acceptance_radius else 'attack1'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame

class FlyingEye(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=100, damage=1, acceptance_radius=40, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Flying Eye."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Take Hit.png", 150, 150, 1, 4)

    def update_behavior(self, player):
        """Flyine Eye chase and attack when close."""
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        new_action = 'idle' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame

# Similar classes for Goblin, Mushroom, and Skeleton
class Goblin(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=75, damage=3, acceptance_radius=30, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Goblin."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Idle.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Run.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Goblin/Take Hit.png", 150, 150, 1, 4)

    def update_behavior(self, player):
        """Goblins chase and attack when close."""
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        new_action = 'run' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame


class Mushroom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=200, damage=5, acceptance_radius=40, scale=2)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Mushroom."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Idle.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Run.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Mushroom/Take Hit.png", 150, 150, 1, 4)

    def update_behavior(self, player):
        """Mushrooms chase and attack when close."""
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        new_action = 'run' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame

class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, health=100, damage=2, acceptance_radius=5, scale=1)
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Skeleton."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Idle.png", 150, 150, 1, 4)
        self.frames['shield'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Shield.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Walk.png", 150, 150, 1, 4)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Take Hit.png", 150, 150, 1, 4)

    def update_behavior(self, player):
        """Skeleton chase and attack when close."""
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        new_action = 'run' if distance > 150 else 'shield' if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame

##
## Special or modified Enemy Behaviour and classes shall be below this .
## I have created BigFlyingEye (mini-boss) for Level 2 .
## I have created MODIFIED Goblins() for Level 1 .
##
class BigFlyingEye(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=0.75, health=200, damage=4, acceptance_radius=100, scale=3)
        self.projectile_image = pygame.image.load("Sprites/Sprites_Effect/Bullets/13.png").convert_alpha()
        self.projectile_image = pygame.transform.scale(self.projectile_image, (60, 36))  # Adjust size as needed
        self.load_frames()
        
        # Enhanced dash mechanics
        self.dash_speed = 5  # Increased dash speed
        self.dash_duration = 60
        self.dash_cooldown = 60  # Reduced cooldown from 240 to 60
        self.is_dashing = False
        self.dash_invincibility = False
        self.dash_vector = (0, 0)  # Initialize dash vector
        
        # New power: Energy Projection
        self.energy_projectile_cooldown = 0
        self.max_energy_projectiles = 3
        self.energy_projectiles = []
        
        # Rage and survival mechanics
        self.shield_count = 2
        self.rage_multiplier = 1.5
        self.original_damage = self.damage
        self.original_speed = self.speed
        
        # Teleport escape mechanism
        self.teleport_cooldown = 0
        self.teleport_threshold = 0.4

    def load_frames(self):
        """Load frames for each action of Big Flying Eye."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Take Hit.png", 150, 150, 1, 4)
        self.frames['charge'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)
        self.frames['dash'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)

    def take_damage(self, damage):
        """Strategic damage taking with teleport escape."""
        # Prevent damage during dash or shield
        if self.is_dashing or self.dash_invincibility:
            return

        # Teleport escape when low on health
        if self.health / 600 < self.teleport_threshold and self.teleport_cooldown <= 0:
            self.teleport_escape()
            return

        # Normal damage taking
        super().take_damage(damage)

    def teleport_escape(self):
        """Teleport to a random location when critically wounded."""
        self.x += random.uniform(-200, 200)
        self.y += random.uniform(-200, 200)
        self.teleport_cooldown = 300  # 5 second cooldown
        self.dash_invincibility = True
        self.dash_duration = 90  # Longer invincibility after teleport

    def start_dash(self, player):
        """Initiate a high-speed dash towards player."""
        if self.dash_cooldown <= 0:
            self.is_dashing = True
            self.dash_duration = 60
            self.dash_invincibility = True
            self.dash_cooldown = 60  # Reduced cooldown
            
            # Calculate dash vector
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            self.dash_vector = (dx/distance * self.dash_speed, dy/distance * self.dash_speed)

    def create_energy_projectile(self, player):
        if self.energy_projectile_cooldown <= 0 and len(self.energy_projectiles) < self.max_energy_projectiles:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
        
            # Normalize direction
            dx, dy = dx/distance, dy/distance
        
            # Calculate angle for rotation
            angle = math.degrees(math.atan2(dy, dx))
            rotated_image = pygame.transform.rotate(self.projectile_image, -angle)
        
            projectile = {
                'x': self.x,
                'y': self.y,
                'dx': dx * 5,
                'dy': dy * 5,
                'damage': 10,
                'image': rotated_image
            }
            self.energy_projectiles.append(projectile)
            self.energy_projectile_cooldown = 180

    def update_energy_projectiles(self, player):
        """Update and manage energy projectiles."""
        if self.energy_projectile_cooldown > 0:
            self.energy_projectile_cooldown -= 1

        # Update existing projectiles
        for projectile in self.energy_projectiles[:]:
            projectile['x'] += projectile['dx']
            projectile['y'] += projectile['dy']
            
            # Check player collision
            projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 10, 10)
            player_rect = pygame.Rect(player.x, player.y, 64, 64)
            
            if projectile_rect.colliderect(player_rect):
                player.health -= projectile['damage']
                self.energy_projectiles.remove(projectile)

    def update_behavior(self, player):
        """Advanced boss behavior with new mechanics."""
        distance = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        # Reduced dash cooldown mechanics
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

        # Dash mechanics
        if self.is_dashing:
            self.x += self.dash_vector[0]
            self.y += self.dash_vector[1]
            
            self.dash_duration -= 1
            if self.dash_duration <= 0:
                self.is_dashing = False
                self.dash_invincibility = False

        # Energy projectile mechanics
        self.update_energy_projectiles(player)

        # Strategic dash and projectile trigger
        if not self.is_dashing:
            if distance < 300 and random.random() < 0.05:  # Increased dash probability
                self.start_dash(player)
            
            if distance < 400 and random.random() < 0.03:
                self.create_energy_projectile(player)

        # Erratic movement
        self.x += random.uniform(-0.5, 0.5)
        self.y += random.uniform(-0.5, 0.5)

        # Determine action and movement
        if distance > 300:
            new_action = 'charge'
            current_speed = self.dash_speed if self.is_dashing else self.speed
        elif distance > self.acceptance_radius:
            new_action = 'idle'
            current_speed = self.speed
        else:
            new_action = 'attack'
            current_speed = self.speed

        # Update action and movement
        if new_action != self.current_action:
            self.current_action = new_action
            self.current_frame = 0

        # Look direction
        self.look_right = player.x > self.x

    def draw(self, surface):
        """Draw the enemy and its energy projectiles."""
        # Draw the boss
        super().draw(surface)
        
        # Draw energy projectiles
        for projectile in self.energy_projectiles:
            surface.blit(projectile['image'], 
                        (projectile['x'] - projectile['image'].get_width()//2, 
                        projectile['y'] - projectile['image'].get_height()//2))
            
class DashingGoblin(Goblin):
    def __init__(self, x, y,speed=1, health=200, damage=3, acceptance_radius=30, scale=1):
        super().__init__(x, y)
        self.dash_cooldown = 3 * 60  # 3 seconds at 60 FPS
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_duration = 1 * 60  # 1 seconds dash duration
        self.dash_speed_multiplier = 3  # 3x speed during dash
        self.dash_direction = (0, 0)

    def update_behavior(self, player):
        """Dashing Goblin chase and periodically dash at player."""
        # Dash cooldown and timer management
        self.dash_timer += 1
        
        # Calculate distance to player
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5
        
        # Determine action based on distance and dash state
        if self.is_dashing:
            # During dash, move in dash direction at high speed
            self.x += self.dash_direction[0] * self.speed * self.dash_speed_multiplier
            self.y += self.dash_direction[1] * self.speed * self.dash_speed_multiplier
            
            # End dash after duration
            if self.dash_timer >= self.dash_cooldown + self.dash_duration:
                self.is_dashing = False
                self.dash_timer = 0
            
            new_action = 'run'
        elif self.dash_timer >= self.dash_cooldown:
            # Initiate dash towards player
            self.is_dashing = True
            
            # Calculate dash direction
            dx = player.x - self.x
            dy = player.y - self.y
            dash_magnitude = (dx**2 + dy**2)**0.5
            
            # Normalize dash direction
            self.dash_direction = (dx/dash_magnitude, dy/dash_magnitude)
            
            new_action = 'run'
        else:
            # Normal movement behavior
            new_action = 'run' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        # Update action and reset frame if changed
        if new_action != self.current_action:
            self.current_action = new_action
            self.current_frame = 0