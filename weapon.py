import pygame
import math

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=5, damage=30):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        
        # Load and scale bullet image
        self.original_image = pygame.image.load("Sprites/Sprites_Effect/Bullets/14.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (48, 48))  # Adjust these numbers for desired size

        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0
        
        # Calculate angle and rotate image
        self.angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, surface):
        surface.blit(self.image, (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2))

class Weapon:
    def __init__(self, name, fire_rate, reload_time, image_path):
        self.name = name
        self.fire_rate = fire_rate  # Shots per second
        self.reload_time = reload_time  # Seconds
        self.last_shot_time = 0
        self.bullets = []
        self.offset = 30  # Distance from player
        self.angle = 0  # Current angle of weapon
        
        # Load weapon image
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((100, 100, 100))
    
    def update_position(self, player_x, player_y, target_x, target_y):
        # Calculate angle to target
        dx = target_x - player_x
        dy = target_y - player_y
        self.angle = math.atan2(dy, dx)
        
        # Position weapon at offset distance from player
        self.x = player_x + math.cos(self.angle) * self.offset
        self.y = player_y + math.sin(self.angle) * self.offset
        
        # Rotate weapon image
        self.rotated_image = pygame.transform.rotate(
            self.image, 
            -math.degrees(self.angle) - 0
        )
        
    def move_with_player(self, player_x, player_y):
        # Keep weapon at current angle but update position with player
        self.x = player_x + math.cos(self.angle) * self.offset
        self.y = player_y + math.sin(self.angle) * self.offset
    
    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time > (1000 / self.fire_rate)
    
    def shoot(self, target_x, target_y):
        if self.can_shoot():
            self.bullets.append(Bullet(self.x, self.y, target_x, target_y))
            self.last_shot_time = pygame.time.get_ticks()
    
    def update_bullets(self, enemies):
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.update()
            
            # Check collision with enemies
            for enemy in enemies:
                if not enemy.is_dead:
                    enemy_rect = pygame.Rect(enemy.x - 25, enemy.y - 25, 50, 50)
                    bullet_rect = pygame.Rect(bullet.x - 2, bullet.y - 2, 4, 4)
                    
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage)
                        bullets_to_remove.append(bullet)
                        break
            
            # Remove bullets that are off screen
            if (bullet.x < 0 or bullet.x > 800 or 
                bullet.y < 0 or bullet.y > 800):
                bullets_to_remove.append(bullet)
        
        # Remove used bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
    
    def draw(self, surface):
        # Draw weapon
        weapon_rect = self.rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(self.rotated_image, weapon_rect)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)

class WeaponManager:
    def __init__(self):
        self.weapons = []
        self.max_weapons = 6
        self.current_weapon = None
        
        # Add initial test weapon
        self.add_weapon("Basic Gun", 5, 1, "Sprites/Sprites_Weapon/Assaut-rifle-4-scoped.png")
        
    def add_weapon(self, name, fire_rate, reload_time, image_path):
        if len(self.weapons) < self.max_weapons:
            weapon = Weapon(name, fire_rate, reload_time, image_path)
            self.weapons.append(weapon)
            if self.current_weapon is None:
                self.current_weapon = weapon
    
    def update(self, player_x, player_y, enemies):
        if not self.current_weapon:
            return
            
        # Get living enemies only
        living_enemies = [e for e in enemies if not e.is_dead]
        
        if living_enemies:
            # Find nearest living enemy
            nearest_enemy = min(living_enemies, 
                key=lambda e: math.sqrt((e.x - player_x)**2 + (e.y - player_y)**2))
            
            # Update weapon position and orientation
            self.current_weapon.update_position(player_x, player_y, 
                                            nearest_enemy.x, nearest_enemy.y)
            
            # Auto-shoot at nearest enemy
            self.current_weapon.shoot(nearest_enemy.x, nearest_enemy.y)
        else:
            # If no living enemies, just move weapon with player at current angle
            self.current_weapon.move_with_player(player_x, player_y)
            
        # Update bullets
        self.current_weapon.update_bullets(enemies)
    
    def draw(self, surface):
        if self.current_weapon:
            self.current_weapon.draw(surface)