import pygame
import math
import random
from queue import PriorityQueue
import player


class StateMachine:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state):
        self.states[name] = state

    def change_state(self, name, enemy, player):
        if self.current_state:
            self.current_state.exit(enemy, player)
        self.current_state = self.states[name]
        self.current_state.enter(enemy, player)

    def update(self, enemy, player):
        if self.current_state:
            new_state = self.current_state.update(enemy, player)
            if new_state:
                self.change_state(new_state.__class__.__name__.lower(), enemy, player)

class AIState:
    def enter(self, enemy, player):
        pass

    def update(self, enemy, player):
        pass

    def exit(self, enemy, player):
        pass

class IdleState(AIState):
    def enter(self, enemy, player):
        """Set the enemy to idle mode when entering this state."""
        enemy.current_action = 'idle'

    def update(self, enemy, player):
        """Check if the player is within detection range and transition to ChaseState."""
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = math.hypot(dx, dy)

        if distance < enemy.lose_aggro_range:
            return ChaseState()  # Transition to chase state if player is close

        return None  # Stay idle if the player is far away


class ChaseState(AIState):
    def enter(self, enemy, player):
        enemy.current_action = 'run'

    def update(self, enemy, player):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = math.hypot(dx, dy)

        if distance < enemy.ranged_attack_range:
            return AttackState()
        elif distance > enemy.lose_aggro_range:
            return IdleState()

        # Pathfinding logic
        if distance >0 :
            enemy.x += dx / distance * enemy.speed
            enemy.y += dy / distance * enemy.speed

        return None


class AttackState(AIState):
    def enter(self, enemy, player):
        enemy.current_action = 'attack'

    def update(self, enemy, player):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = math.hypot(dx, dy)

        if distance > enemy.ranged_attack_range * 1.2:
            return ChaseState()


        if distance <= enemy.ranged_attack_range:
            enemy.shoot_projectile(player.x, player.y)  # now fires a burst of 3 projectiles

        return None


class TacticalRetreatState(AIState):
    def enter(self, enemy, player):
        enemy.current_action = 'run'
        self.retreat_direction = random.choice([-1, 1])

    def update(self, enemy, player):
        # Move perpendicular to player direction
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        tangent_x = -dy * self.retreat_direction
        tangent_y = dx * self.retreat_direction

        enemy.x += tangent_x * enemy.speed
        enemy.y += tangent_y * enemy.speed

        if enemy.health > enemy.max_health * 0.3:
            return ChaseState()

        return None


class Enemy:
    def __init__(self, x, y, speed, health, damage, acceptance_radius, scale=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.max_health = health
        self.damage = damage  # Damage per second
        self.acceptance_radius = acceptance_radius  # Stop moving when within this distance
        self.scale = scale
        self.frames = {}  # Dictionary to hold frames for different actions
        self.current_action = 'idle'
        self.previous_action = None  # Track previous action 
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 10  # Adjust for animation speed
        self.look_right = True
        ##For death
        self.is_dead = False
        self.is_taking_hit = False
        self.hit_animation_timer = 0
        self.death_animation_completed = False
        self.ai_state = None
        self.last_player_position = (0, 0)
        self.lose_aggro_range = 500
        self.attack_cooldown = 0
        self.patrol_path = []
        self.current_patrol_point = 0
        self.obstacle_map = None
        self.fov = 120  # Field of view in degrees

        # Add AI states
        self.state_machine = StateMachine()
        self.state_machine.add_state('chase', ChaseState())
        self.state_machine.add_state('attack', AttackState())
        self.state_machine.add_state('retreat', TacticalRetreatState())

        # Ranged attack properties
        self.ranged_attack_cooldown = 0
        self.ranged_attack_range = 600  # Distance at which the enemy will use ranged attacks
        self.projectile_speed = 10
        self.projectiles = []  # List to store active projectiles

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
                self.hit_animation_timer = len(
                    self.frames['takehit']) * self.frame_delay  # Adjust based on animation length

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
        self.state_machine.update(self, player)
        # Calculate the player's center and enemy's center
        player_center = (player.x, player.y)
        enemy_center = (self.x, self.y)

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

            # Update direction only when moving
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

        # Decrement the ranged attack cooldown if it is active.
        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 0.5

        # Update projectiles
        self.update_projectiles(player)

    def has_line_of_sight(self, player):
        # Convert positions to grid indices
        x0, y0 = int(self.x // 16), int(self.y // 16)
        x1, y1 = int(player.x // 16), int(player.y // 16)

        # Ensure x and y are within valid range
        max_x = len(self.obstacle_map[0]) - 1
        max_y = len(self.obstacle_map) - 1

        x0, y0 = max(0, min(x0, max_x)), max(0, min(y0, max_y))
        x1, y1 = max(0, min(x1, max_x)), max(0, min(y1, max_y))

        # Use correct matrix indexing
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                if self.obstacle_map[y][x]:  # Only check within valid range
                    return False
        return True

    def pathfind_to_player(self, player):
        """A* pathfinding implementation with grid-based coordinates"""
        # Convert pixel positions to grid coordinates
        start_x = int(self.x // 16)
        start_y = int(self.y // 16)
        goal_x = int(player.x // 16)
        goal_y = int(player.y // 16)
        
        start = (start_x, start_y)
        goal = (goal_x, goal_y)
        
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == goal:
                break
                
            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        # Reconstruct path and convert back to pixel coordinates
        path = []
        current = goal
        while current != start:
            path.append((
                current[0] * 16 + 16//2,
                current[1] * 16 + 16//2
            ))
            current = came_from.get(current, start)  # Fallback to start if path not found
        path.reverse()
        return path
    
    def update_projectiles(self, player):
        """Update the position of projectiles and check for collisions with the player."""
        for projectile in self.projectiles[:]:
            projectile['x'] += projectile['dx']
            projectile['y'] += projectile['dy']

            # Remove projectiles after they travel 1500 pixels from origin
            distance_traveled = math.hypot(projectile['x'] - self.x, projectile['y'] - self.y)
            if distance_traveled > 1500:
                self.projectiles.remove(projectile)
                continue

            # Check collision with player
            projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 10, 10)
            player_rect = pygame.Rect(player.x, player.y, 64, 64)
            if projectile_rect.colliderect(player_rect):
                player.health -= projectile['damage']
                self.projectiles.remove(projectile)

    def shoot_projectile(self, target_x, target_y):
        """Shoot a projectile towards specified coordinates with safety checks"""
        if self.ranged_attack_cooldown <= 0:
            # Calculate direction to target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)

            # Prevent division by zero
            if distance == 0:
                return  # Can't shoot if already at target position

            # Normalize direction vector
            dx /= distance
            dy /= distance

            # Create projectile dictionary
            projectile = {
                'x': self.x,
                'y': self.y,
                'dx': dx * self.projectile_speed,
                'dy': dy * self.projectile_speed,
                'damage': self.damage,
                'image': self.projectile_image
            }

            # Add to projectiles list and reset cooldown to 2 seconds (120 frames)
            self.projectiles.append(projectile)
            self.ranged_attack_cooldown = 120  # 2 second cooldown at 60 FPS

    def update_behavior(self, player):
        """Default enemy behavior (to be overridden by subclasses)."""
        pass
        def update_ai(self, player):
            """Enhanced AI decision-making"""
        if self.health < self.max_health * 0.3 and random.random() < 0.1:
            self._execute_tactical_retreat(player)
        else:
            self._execute_adaptive_attack(player)
        pass
            
    def _execute_adaptive_attack(self, player):
        """Choose attack pattern based on situation"""
        distance = self.distance_to(player)
        
        if distance < self.melee_range:
            self.melee_attack(player)
        elif distance < self.ranged_range:
            if random.random() < 0.7:  # 70% chance for aimed shot
                self.predictive_ranged_attack(player)
            else:  # 30% chance for spread shot
                self.spread_attack(player, 3, 15)
                
    def predictive_ranged_attack(self, player):
        """Lead shots based on player movement"""
        travel_time = self.distance_to(player) / self.projectile_speed
        predicted_x = player.x + player.dx * travel_time
        predicted_y = player.y + player.dy * travel_time
        self.shoot_projectile(predicted_x, predicted_y)
        
    def spread_attack(self, player, num_shots, spread_angle):
        """Fan-shaped projectile spread"""
        base_angle = math.degrees(math.atan2(player.y-self.y, player.x-self.x))
        for i in range(num_shots):
            angle = base_angle + spread_angle * (i - num_shots//2)
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            self.shoot_projectile(self.x + dx*50, self.y + dy*50)


    def draw(self, surface):
        """Draw the enemy, handling boss rendering separately."""
        if self.current_action not in self.frames:
            print(f"Warning: Missing animation frames for action '{self.current_action}' in {type(self).__name__}")
            return  # Skip drawing if frames are missing

        sprite = self.frames[self.current_action][self.current_frame]

        if not self.look_right:
            sprite = pygame.transform.flip(sprite, True, False)
        sprite_rect = sprite.get_rect(center=(self.x, self.y))

        # Draw the sprite
        surface.blit(sprite, sprite_rect.topleft)

    def get_neighbors(self, pos):
        """Get valid neighboring positions for pathfinding"""
        x, y = pos
        neighbors = [
            (x + 1, y),  # Right
            (x - 1, y),  # Left
            (x, y + 1),  # Down
            (x, y - 1)   # Up
        ]
        
        # Filter valid neighbors within map bounds and not blocked
        valid_neighbors = []
        for nx, ny in neighbors:
            if 0 <= nx < 44 and 0 <= ny < 44:
                if not self.obstacle_map[ny][nx]:  # Note: obstacle_map is [y][x]
                    valid_neighbors.append((nx, ny))
        return valid_neighbors

    def heuristic(self, a, b):
        """Manhattan distance heuristic for A* pathfinding"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class EnemySquad:
    def __init__(self):
        self.members = []
        self.formation_positions = []
        self.current_strategy = "flank"
    
    def update_squad_behavior(self, player):
        if self.current_strategy == "flank":
            self.execute_flanking(player)
        elif self.current_strategy == "swarm":
            self.execute_swarming(player)
        elif self.current_strategy == "cover":
            self.execute_cover_fire(player)
    
    def execute_flanking(self, player):
        main_attackers = self.members[:len(self.members)//2]
        flankers = self.members[len(self.members)//2:]
        
        # Main group engages frontally
        for enemy in main_attackers:
            enemy.state_machine.change_state('attack')
        
        # Flankers move to sides
        for i, enemy in enumerate(flankers):
            angle = 90 * (-1 if i % 2 else 1)
            flank_position = (
                player.x + math.cos(math.radians(angle)) * 200,
                player.y + math.sin(math.radians(angle)) * 200
            )
            enemy.move_to(flank_position)
    def move_to(self, position):
        self.x, self.y = position


class EnemySwarm:
    def __init__(self, members):
        self.members = members
        self.strategy = "flank"
        
    def update_squad_behavior(self, player, obstacle_map):
        if self.strategy == "flank":
            self._execute_flanking(player)
        elif self.strategy == "swarm":
            self._execute_swarming(player)
        elif self.strategy == "cover":
            self._execute_cover_fire(player, obstacle_map)

    def _execute_flanking(self, player):
        # Intelligent flanking positions
        flank_angle = 45  # Degrees from center
        flank_distance = 150  # Pixels from player
        
        for i, enemy in enumerate(self.members):
            angle = flank_angle * (-1 if i%2 else 1)
            target_x = player.x + math.cos(math.radians(angle)) * flank_distance
            target_y = player.y + math.sin(math.radians(angle)) * flank_distance
            enemy.move_to((target_x, target_y))
            
            if enemy.distance_to(player) < enemy.attack_range:
                enemy.attack(player)

    def _execute_cover_fire(self, player, obstacle_map):
        # Find cover positions
        cover_positions = self._find_cover_positions(player, obstacle_map)
        for enemy, position in zip(self.members, cover_positions):
            enemy.move_to(position)
            if enemy.has_line_of_sight(player):
                enemy.ranged_attack(player)

# Basic enemy classes with their own load_frames functions
class EvilWizard(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=0.75, health=200, damage=2.5, acceptance_radius=10, scale=1.5)
        self.projectile_image = pygame.image.load("Sprites/Sprites_Effect/Bullets/13.png").convert_alpha()
        self.projectile_image = pygame.transform.scale(self.projectile_image, (30, 18))  # Adjust size as needed
        self.ranged_attack_range = 600  # Even longer range for wizard
        self.projectile_speed = 10  # Faster projectiles
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

        # Shoot projectiles if in range
        if distance < self.ranged_attack_range:
            self.shoot_projectile(player.x,player.y)
        # Line of sight check
        if self.has_line_of_sight(player):
            # Advanced spell patterns
            if self.attack_cooldown <= 0:
                self.cast_spread_spell(player)
                self.attack_cooldown = 45
            else:
                self.attack_cooldown -= 1



            # Summon minions when damaged
            if self.health < self.max_health * 0.5 and not self.has_summoned:
                self.summon_minions()
                self.has_summoned = True

    def cast_spread_spell(self, target):
        for angle in range(-30, 31, 15):
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            self.shoot_projectile(target.x + dx * 50, target.y + dy * 50)

    def distance_to(self, target):
        """Calculate Euclidean distance to a target (player or object)."""
        return ((self.x - target.x) ** 2 + (self.y - target.y) ** 2) ** 0.5

    def draw(self, surface):
        """Draw the current frame of the enemy on the screen."""
        if self.current_action not in self.frames:
            print(f"Warning: Missing animation frames for action '{self.current_action}' in {type(self).__name__}")
            return  # Skip drawing if frames are missing

        sprite = self.frames[self.current_action][self.current_frame]

        if not self.look_right:
            sprite = pygame.transform.flip(sprite, True, False)
        sprite_rect = sprite.get_rect(center=(self.x, self.y))

        # Draw the sprite
        surface.blit(sprite, sprite_rect.topleft)


class FlyingEye(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=0.75, health=100, damage=0.5, acceptance_radius=40, scale=1)
        self.projectile_image = pygame.image.load("Sprites/Sprites_Effect/Bullets/29.png").convert_alpha()
        self.projectile_image = pygame.transform.scale(self.projectile_image, (30, 18))  # Adjust size as needed
        self.load_frames()

    def load_frames(self):
        """Load frames for each action of Flying Eye."""
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Flight.png", 150, 150, 1, 8)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Flying eye/Take Hit.png", 150, 150, 1, 4)

    def update_behavior(self, player):
        """Flying Eye chase and attack when close."""
        distance = math.hypot(player.x - self.x, player.y - self.y)
        
        # Fix incorrect condition
        new_action = 'idle' if distance > 150 else 'idle'  if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame

        # Shoot projectiles if in range
        if distance < self.ranged_attack_range:
            self.shoot_projectile(player.x, player.y)  # FIX: Pass (x, y) instead of player object

        # Circular strafing pattern
        angle = pygame.time.get_ticks() * 0.001  # Continuous rotation
        radius = 150

        target_x = player.x + math.cos(angle) * radius
        target_y = player.y + math.sin(angle) * radius

        dx = target_x - self.x
        dy = target_y - self.y
        move_distance = math.hypot(dx, dy)

        if move_distance > 10:
            self.x += dx / move_distance * self.speed
            self.y += dy / move_distance * self.speed

        # Predictive leading shots
        if self.attack_cooldown <= 0:
            self.predictive_shot(player)
            self.attack_cooldown = 60


    def predictive_shot(self, player):
        """Predicts where the player will be and shoots a projectile towards that position."""
        distance = self.distance_to(player)

        if distance == 0 or self.projectile_speed == 0:
            # Avoid division by zero, shoot directly at player
            self.shoot_projectile(player.x, player.y)
            return

        time_to_target = distance / self.projectile_speed

        # Handle missing dx and dy safely, default to 0
        player_dx = getattr(player, "dx", 0)
        player_dy = getattr(player, "dy", 0)

        # Predict future position
        future_x = player.x + (player_dx * time_to_target)
        future_y = player.y + (player_dy * time_to_target)

        # If player is stationary, shoot at the current position
        if player_dx == 0 and player_dy == 0:
            future_x, future_y = player.x, player.y

        self.shoot_projectile(future_x, future_y)  # Now correctly calls the updated method

    def distance_to(self, target):
        """Calculate Euclidean distance to a target (player or object)."""
        return ((self.x - target.x) ** 2 + (self.y - target.y) ** 2) ** 0.5
    
    def draw(self, surface):
        """Draw the current frame of the enemy on the screen."""
        super().draw(surface)
        # Draw projectiles
        for projectile in self.projectiles:
            projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 10, 10)

            # Load the projectile image and animate it
            rotated_projectile = pygame.transform.rotate(projectile['image'],
                                                         -math.degrees(math.atan2(projectile['dy'], projectile['dx'])))
            surface.blit(rotated_projectile, projectile_rect.topleft)


# Similar classes for Goblin, Mushroom, and Skeleton
class Goblin(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=0.75, health=75, damage=1.5, acceptance_radius=30, scale=1)
        self.load_frames()
    def distance_to(self, target):
        """Calculate Euclidean distance to a target (player or object)."""
        return ((self.x - target.x) ** 2 + (self.y - target.y) ** 2) ** 0.5


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
        new_action = 'idle' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        if new_action != self.current_action:  # Only change if different
            self.current_action = new_action
            self.current_frame = 0  # Reset animation frame


class Mushroom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1.25, health=200, damage=2.5, acceptance_radius=40, scale=2)
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

        self.shield_active = False
        self.shield_duration = 180
        self.shield_cooldown = 600
        self.shield_timer = 0
        self.shield_cooldown_timer = 0

    def load_frames(self):
        self.frames['attack'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Attack.png", 150, 150, 1, 8)
        self.frames['death'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Death.png", 150, 150, 1, 4)
        self.frames['idle'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Idle.png", 150, 150, 1, 4)
        self.frames['shield'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Shield.png", 150, 150, 1, 4)
        self.frames['run'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Walk.png", 150, 150, 1, 4)
        self.frames['takehit'] = self.load_frame_sheet("Sprites/Sprites_Enemy/Skeleton/Take Hit.png", 150, 150, 1, 4)

    def take_damage(self, damage):
        if self.shield_active:
            return
        super().take_damage(damage)

    def activate_shield(self):
        if self.shield_cooldown_timer == 0:
            self.shield_active = True
            self.shield_timer = self.shield_duration
            self.current_action = 'shield'
            self.current_frame = 0

    def update_behavior(self, player):
        distance = ((player.x - self.x) ** 2 + (player.y - self.y) ** 2) ** 0.5

        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                self.shield_cooldown_timer = self.shield_cooldown
            return

        if self.shield_cooldown_timer > 0:
            self.shield_cooldown_timer -= 1
        elif self.health < 50 and random.random() < 0.1:
            self.activate_shield()

        new_action = 'run' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'
        if new_action != self.current_action:
            self.current_action = new_action
            self.current_frame = 0
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
            distance = math.sqrt(dx ** 2 + dy ** 2)
            self.dash_vector = (dx / distance * self.dash_speed, dy / distance * self.dash_speed)

    def create_energy_projectile(self, player):
        if self.energy_projectile_cooldown <= 0 and len(self.energy_projectiles) < self.max_energy_projectiles:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Normalize direction
            dx, dy = dx / distance, dy / distance

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
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)

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
                         (projectile['x'] - projectile['image'].get_width() // 2,
                          projectile['y'] - projectile['image'].get_height() // 2))


class DashingGoblin(Goblin):
    def __init__(self, x, y, speed=1, health=200, damage=1.5, acceptance_radius=30, scale=1):
        super().__init__(x, y)
        self.dash_cooldown = 3 * 60  # 3 seconds at 60 FPS
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_duration = 1 * 60  # 1 second dash duration
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

            new_action = 'idle'  # Use 'idle' as a fallback if 'run' is not available
        elif self.dash_timer >= self.dash_cooldown:
            # Initiate dash towards player
            self.is_dashing = True

            # Calculate dash direction
            dx = player.x - self.x
            dy = player.y - self.y
            dash_magnitude = (dx ** 2 + dy ** 2) ** 0.5

            # Normalize dash direction
            self.dash_direction = (dx / dash_magnitude, dy / dash_magnitude)

            new_action = 'idle'  # Use 'idle' as a fallback if 'run' is not available
        else:
            # Normal movement behavior
            new_action = 'idle' if distance > 150 else 'idle' if distance > self.acceptance_radius else 'attack'

        # Update action and reset frame if changed
        if new_action != self.current_action:
            self.current_action = new_action
            self.current_frame = 0


    def draw(self, surface):
        """Draw the current frame of the enemy on the screen."""
        if self.current_action not in self.frames:
            print(f"Warning: Missing animation frames for action '{self.current_action}' in {type(self).__name__}")
            return  # Skip drawing if frames are missing

        sprite = self.frames[self.current_action][self.current_frame]

        if not self.look_right:
            sprite = pygame.transform.flip(sprite, True, False)
        sprite_rect = sprite.get_rect(center=(self.x, self.y))

        # Draw the sprite
        surface.blit(sprite, sprite_rect.topleft)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 10, 10)

            # Load the projectile image and animate it
            rotated_projectile = pygame.transform.rotate(projectile['image'],
                                                         -math.degrees(math.atan2(projectile['dy'], projectile['dx'])))
            surface.blit(rotated_projectile, projectile_rect.topleft)
            

class TeleportingMushroom(Mushroom):

    def __init__(self, x, y):
            super().__init__(x, y)
            self.teleport_timer = 0

    def update(self, player):
        super().update(player)
        self.teleport_timer += 1
        if self.teleport_timer > 200:
            self.teleport(player)
            self.teleport_timer = 0

    def teleport(self, player):
        """Teleport to a random position."""
        self.x = player.x + random.randint(5, 50)
        self.y = player.y + random.randint(5, 30)
